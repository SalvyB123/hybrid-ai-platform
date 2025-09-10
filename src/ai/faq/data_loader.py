from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class FAQItem(BaseModel):
    id: str
    question: str
    answer: str
    tags: list[str] | None = None


def load_faqs(path: str | Path = "data/faqs.yaml") -> list[FAQItem]:
    p = Path(path)
    if not p.exists():
        return []
    with p.open("r") as f:
        raw = yaml.safe_load(f) or []
    return [FAQItem(**item) for item in raw]
