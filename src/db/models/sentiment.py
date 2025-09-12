from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class Sentiment(Base):
    __tablename__ = "sentiment"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.dialects.postgresql.UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    text: Mapped[str] = mapped_column(sa.Text(), nullable=False)
    score: Mapped[float] = mapped_column(sa.Float(), nullable=False)
    label: Mapped[str] = mapped_column(sa.String(length=16), nullable=False)

    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        nullable=False,
    )

    __table_args__ = (
        sa.CheckConstraint(
            "label in ('positive','negative','neutral')",
            name="ck_sentiment_label",
        ),
        sa.Index("ix_sentiment_created_at", "created_at"),
        sa.Index("ix_sentiment_label", "label"),
    )
