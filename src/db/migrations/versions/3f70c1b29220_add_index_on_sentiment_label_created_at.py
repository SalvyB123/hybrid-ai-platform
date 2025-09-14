"""add index on sentiment(label, created_at)

Revision ID: 3f70c1b29220
Revises: 9ddf87711437
Create Date: 2025-09-14 00:00:00.000000
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f70c1b29220"
down_revision: str | Sequence[str] | None = "9ddf87711437"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Composite index to optimise queries like:
    # SELECT ... FROM sentiment WHERE label = ? ORDER BY created_at DESC LIMIT k;
    op.create_index(
        "ix_sentiment_label_created_at",
        "sentiment",
        ["label", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_sentiment_label_created_at", table_name="sentiment")
