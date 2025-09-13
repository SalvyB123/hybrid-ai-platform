from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Input text to analyse")


class SentimentResponse(BaseModel):
    id: UUID
    text: str
    score: float
    label: Literal["positive", "negative", "neutral"]
