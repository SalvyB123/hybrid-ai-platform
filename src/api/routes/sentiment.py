from __future__ import annotations

from typing import Annotated  # add this import

from fastapi import APIRouter, Depends, HTTPException, status
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
    db: Annotated[AsyncSession, Depends(get_db)],  # <-- no default call; satisfies B008
) -> SentimentResponse:
    text = payload.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Text must not be empty.",
        )

    result = classify(text)

    row = Sentiment(text=text, score=result.score, label=result.label)
    db.add(row)
    await db.flush()
    await db.commit()
    await db.refresh(row)

    return SentimentResponse(id=row.id, text=row.text, score=row.score, label=row.label)
