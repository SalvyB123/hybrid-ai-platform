from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.ai.sentiment import classify
from src.api.schemas.sentiment import (
    SentimentRequest,
    SentimentResponse,
    SentimentSummaryResponse,
)
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


@router.get(
    "/summary",
    response_model=SentimentSummaryResponse,
    summary="Return counts by sentiment label for dashboard",
)
async def get_sentiment_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SentimentSummaryResponse:
    """
    Aggregate sentiment results by label.
    Returns zeros for missing buckets so the UI contract is stable.
    """
    stmt = select(Sentiment.label, func.count()).group_by(Sentiment.label)
    res = await db.execute(stmt)

    buckets = {"positive": 0, "negative": 0, "neutral": 0}
    for label, count in res.all():
        # Defensive cast to int; asyncpg returns Decimal/Int variants
        if label in buckets:
            buckets[label] = int(count)

    total = sum(buckets.values())
    return SentimentSummaryResponse(**buckets, total=total)
