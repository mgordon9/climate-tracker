from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import rag

router = APIRouter()


class QARequest(BaseModel):
    country_id: int
    question: str


class SourceRef(BaseModel):
    title: str
    excerpt: str


class QAResponse(BaseModel):
    answer: str
    sources: list[SourceRef]


@router.post("/qa", response_model=QAResponse)
def qa_endpoint(body: QARequest, db: Session = Depends(get_db)) -> QAResponse:
    if not body.question.strip():
        raise HTTPException(status_code=422, detail="Question must not be empty.")
    result = rag.answer_question(db, body.country_id, body.question)
    return QAResponse(
        answer=result["answer"],
        sources=[SourceRef(**s) for s in result["sources"]],
    )
