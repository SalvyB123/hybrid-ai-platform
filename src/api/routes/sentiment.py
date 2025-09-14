from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.sentiment import classify
from src.api.schemas.sentiment import SentimentRequest, SentimentResponse
from src.db.models.sentiment import Sentiment
from src.db.session import get_db

router = APIRouter(prefix="/sentiment", tags=["sentiment"])


@router.post(
    "",
    response_model=SentimentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyse sentiment and persist result",
)
async def create_sentiment(
    payload: SentimentRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SentimentResponse:
    # Input validation (min/max length) is handled by SentimentRequest
    text = payload.text.strip()

    # Classify
    result = classify(text)

    # Persist
    row = Sentiment(text=text, score=result.score, label=result.label)
    db.add(row)
    await db.flush()
    await db.commit()
    await db.refresh(row)

    return SentimentResponse(id=row.id, text=row.text, score=row.score, label=row.label)
