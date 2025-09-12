"""create sentiment table

Revision ID: 9ddf87711437
Revises: 1130532299a8
Create Date: 2025-09-12 07:14:11.958172

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9ddf87711437"
down_revision: str | Sequence[str] | None = "1130532299a8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sentiment",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("label", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "label in ('positive','negative','neutral')",
            name="ck_sentiment_label",
        ),
    )

    op.create_index(
        "ix_sentiment_created_at",
        "sentiment",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_sentiment_label",
        "sentiment",
        ["label"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_sentiment_label", table_name="sentiment")
    op.drop_index("ix_sentiment_created_at", table_name="sentiment")
    op.drop_table("sentiment")
