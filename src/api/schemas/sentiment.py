from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class SentimentRequest(BaseModel):
    # Enforce basic limits to prevent abuse and make validation deterministic
    text: str = Field(..., min_length=1, max_length=2000)


class SentimentResponse(BaseModel):
    id: UUID
    text: str
    score: float
    label: Literal["positive", "negative", "neutral"]
