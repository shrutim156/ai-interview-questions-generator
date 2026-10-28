from pydantic import BaseModel, Field
from typing import List, Optional

class QuestionGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=100)
    target_role: str = Field("General Software Engineer")
    difficulty: str = Field("Intermediate")
    num_questions: int = Field(5, ge=1, le=30, description="Number of questions (1-30)")

class QuestionItem(BaseModel):
    id: int
    question: str
    hint: Optional[str] = None

class QuestionGenerateResponse(BaseModel):
    session_id: str
    topic: str
    target_role: str
    difficulty: str
    total_questions: int
    questions: List[QuestionItem]

class DetailRequest(BaseModel):
    session_id: str
    question_id: int

class AnswerResponse(BaseModel):
    question_id: int
    model_answer: str

class CodeResponse(BaseModel):
    question_id: int
    code_example: str