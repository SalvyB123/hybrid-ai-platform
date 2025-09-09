from __future__ import annotations
from pydantic import BaseModel
from typing import Annotated
from pydantic import StringConstraints

Question = Annotated[str, StringConstraints(min_length=1, max_length=500)]


class FAQAskRequest(BaseModel):
    question: Question


class FAQAnswer(BaseModel):
    answer: str
    score: float
    source_id: str


class FAQHandoff(BaseModel):
    handoff: bool = True
    score: float
    question: str
