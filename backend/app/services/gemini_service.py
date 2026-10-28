import json
import time
import uuid
import traceback
from typing import Dict, Any, Optional, List

from google import genai
from google.genai import types

from app.config import settings

# Ordered priority list for model fallback
MODEL_PRIORITY: List[str] = [
    "models/gemini-3.7-flash",
    "models/gemini-3.6-flash",
    "models/gemini-3.5-flash",
    "models/gemini-3.5-flash-lite",
]


class GeminiService:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )
        # Active session store for on-demand details (answers & code)
        self._sessions: Dict[str, Dict[str, Any]] = {}

        # Pool cache format: { "topic:role:difficulty": [ { "question": ..., "hint": ... }, ... ] }
        self._question_pool: Dict[str, List[Dict[str, str]]] = {}

    def _generate_content_with_fallback(
        self,
        contents: str,
        config: Optional[types.GenerateContentConfig] = None,
    ) -> Any:
        last_exception = None

        for model_name in MODEL_PRIORITY:
            try:
                print(f"[GeminiService] Attempting generation with model: {model_name}")
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )
                print(f"[GeminiService] Successfully generated response using: {model_name}")
                return response
            except Exception as e:
                err_msg = str(e)
                last_exception = e
                if "503" in err_msg or "UNAVAILABLE" in err_msg or "resource_exhausted" in err_msg.lower():
                    print(f"[GeminiService] Model '{model_name}' unavailable (503). Retrying with next model...")
                    continue
                else:
                    print(f"[GeminiService] Critical error with model '{model_name}': {err_msg}")
                    raise e

        raise RuntimeError(
            f"All fallback models failed. Last error: {str(last_exception)}"
        ) from last_exception

    def _get_pool_key(self, topic: str, target_role: str, difficulty: str) -> str:
        return f"{topic.strip().lower()}:{target_role.strip().lower()}:{difficulty.strip().lower()}"

    async def generate_questions_only(
        self,
        topic: str,
        target_role: str,
        difficulty: str,
        count: int,
    ) -> dict:
        pool_key = self._get_pool_key(topic, target_role, difficulty)
        cached_items = self._question_pool.get(pool_key, [])

        selected_questions: List[Dict[str, str]] = []

        # 1. Use questions from the pool if available
        if cached_items:
            take_count = min(len(cached_items), count)
            selected_questions.extend(cached_items[:take_count])
            # Remove served items from the pool
            self._question_pool[pool_key] = cached_items[take_count:]
            print(f"[Question Pool] Served {take_count} question(s) directly from memory pool cache.")

        needed_count = count - len(selected_questions)

        # 2. If we still need more questions, request a batch from Gemini (at least 5 to keep pool stocked)
        if needed_count > 0:
            fetch_count = max(needed_count, 5)
            prompt = f"""
You are a senior technical interviewer.

Generate {fetch_count} interview questions for a {target_role}.

Topic: {topic}
Difficulty: {difficulty}

Provide ONLY the question title and a brief hint for each.
Do NOT generate full model answers or code examples.

Return ONLY valid JSON matching this exact structure:
{{
    "questions": [
        {{
            "id": 1,
            "question": "Question text here?",
            "hint": "Brief hint here"
        }}
    ]
}}
"""
            try:
                print(f"\n========== GENERATING {fetch_count} QUESTIONS VIA GEMINI ==========\n")
                start = time.time()

                response = self._generate_content_with_fallback(
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    ),
                )
                end = time.time()
                print(f"\nGemini Questions API Time: {end - start:.2f} seconds\n")

                if not response.text:
                    raise RuntimeError("Gemini returned an empty response.")

                data = json.loads(response.text)
                new_items = data.get("questions", [])

                # Append needed items to selected_questions
                selected_questions.extend(new_items[:needed_count])

                # Store excess questions in pool cache for future instant requests
                excess_items = new_items[needed_count:]
                if excess_items:
                    if pool_key not in self._question_pool:
                        self._question_pool[pool_key] = []
                    self._question_pool[pool_key].extend(excess_items)
                    print(f"[Question Pool] Added {len(excess_items)} extra question(s) to cache pool.")

            except Exception:
                print("\n========== GEMINI ERROR ==========\n")
                traceback.print_exc()
                print("\n=================================\n")
                raise

        # 3. Build session data with stable integer IDs
        session_id = str(uuid.uuid4())
        questions_dict = {}

        for idx, item in enumerate(selected_questions, start=1):
            questions_dict[idx] = {
                "id": idx,
                "question": item.get("question", ""),
                "hint": item.get("hint"),
                "model_answer": None,
                "code_example": None,
            }

        # Cache session details for on-demand answer/code fetching
        self._sessions[session_id] = {
            "topic": topic,
            "target_role": target_role,
            "difficulty": difficulty,
            "questions": questions_dict,
        }

        return {
            "session_id": session_id,
            "topic": topic,
            "target_role": target_role,
            "difficulty": difficulty,
            "total_questions": len(questions_dict),
            "questions": list(questions_dict.values()),
        }

    async def get_or_generate_answer(self, session_id: str, question_id: int) -> str:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found or expired.")

        q_data = session["questions"].get(question_id)
        if not q_data:
            raise KeyError(f"Question ID {question_id} not found in session.")

        if q_data["model_answer"]:
            return q_data["model_answer"]

        prompt = f"""
You are an expert technical interviewer.

Target Role: {session['target_role']}
Topic: {session['topic']}

Question: "{q_data['question']}"

Provide a clear, thorough, and high-quality model answer to this interview question.
Do not wrap response in JSON. Output direct markdown formatting suitable for an answer box.
"""
        try:
            response = self._generate_content_with_fallback(contents=prompt)
            answer = response.text.strip() if response.text else "No answer returned."
            q_data["model_answer"] = answer
            return answer
        except Exception:
            traceback.print_exc()
            raise

    async def get_or_generate_code(self, session_id: str, question_id: int) -> str:
        session = self._sessions.get(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found or expired.")

        q_data = session["questions"].get(question_id)
        if not q_data:
            raise KeyError(f"Question ID {question_id} not found in session.")

        if q_data["code_example"]:
            return q_data["code_example"]

        prompt = f"""
You are an expert software developer.

Topic: {session['topic']}
Question: "{q_data['question']}"

Provide a concise, practical code example or code solution demonstrating the answer to this question.
Output code directly (clean formatted code snippet).
"""
        try:
            response = self._generate_content_with_fallback(contents=prompt)
            code = response.text.strip() if response.text else "// No code snippet generated."
            q_data["code_example"] = code
            return code
        except Exception:
            traceback.print_exc()
            raise