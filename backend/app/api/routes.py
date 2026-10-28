import traceback
from fastapi import APIRouter, HTTPException, status

from app.schemas.question import (
    QuestionGenerateRequest,
    QuestionGenerateResponse,
    DetailRequest,
    AnswerResponse,
    CodeResponse,
)
from app.services.gemini_service import GeminiService

router = APIRouter()
gemini_service = GeminiService()


@router.post(
    "/generate-questions",
    response_model=QuestionGenerateResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_questions(payload: QuestionGenerateRequest):
    try:
        data = await gemini_service.generate_questions_only(
            topic=payload.topic,
            target_role=payload.target_role,
            difficulty=payload.difficulty,
            count=payload.num_questions,
        )
        return data
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )


@router.post(
    "/generate-answer",
    response_model=AnswerResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_answer(payload: DetailRequest):
    try:
        answer = await gemini_service.get_or_generate_answer(
            session_id=payload.session_id,
            question_id=payload.question_id,
        )
        return AnswerResponse(question_id=payload.question_id, model_answer=answer)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )


@router.post(
    "/generate-code",
    response_model=CodeResponse,
    status_code=status.HTTP_200_OK,
)
async def generate_code(payload: DetailRequest):
    try:
        code = await gemini_service.get_or_generate_code(
            session_id=payload.session_id,
            question_id=payload.question_id,
        )
        return CodeResponse(question_id=payload.question_id, code_example=code)
    except KeyError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )