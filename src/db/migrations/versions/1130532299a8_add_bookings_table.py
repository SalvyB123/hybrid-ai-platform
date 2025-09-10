"""add bookings table

Revision ID: 1130532299a8
Revises: eaef555dd67b
Create Date: 2025-09-04 07:37:29.971325

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1130532299a8"
down_revision: str | Sequence[str] | None = "c2d71659ed53"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("customer_name", sa.String(length=120), nullable=False),
        sa.Column("customer_email", sa.String(length=254), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "confirmed", "cancelled", name="booking_status"),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_bookings_customer_email", "bookings", ["customer_email"], unique=False)
    op.create_index("ix_bookings_starts_at", "bookings", ["starts_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_bookings_starts_at", table_name="bookings")
    op.drop_index("ix_bookings_customer_email", table_name="bookings")
    op.drop_table("bookings")
    # optional: also drop the enum if you won’t reuse it elsewhere
    # op.execute("DROP TYPE IF EXISTS booking_status")
