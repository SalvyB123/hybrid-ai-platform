# src/api/schemas/faq.py
from __future__ import annotations
from pydantic import BaseModel, Field


class FAQAskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class FAQAnswer(BaseModel):
    answer: str
    score: float
    source_id: str
