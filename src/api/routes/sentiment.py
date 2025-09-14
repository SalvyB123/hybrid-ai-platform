from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
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
    """
    Classify the sentiment of the provided text and persist the result.
    Rolls back and returns 500 on DB failures so the global error handler
    can wrap the response in the standard error envelope.
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Text must not be empty.",
        )

    result = classify(text)
    row = Sentiment(text=text, score=result.score, label=result.label)
    db.add(row)

    try:
        await db.flush()
        await db.commit()
    except SQLAlchemyError as err:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to persist sentiment result.",
        ) from err

    await db.refresh(row)
    return SentimentResponse(id=row.id, text=row.text, score=row.score, label=row.label)
