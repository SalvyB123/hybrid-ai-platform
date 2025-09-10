from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from src.api.schemas.booking import BookingCreate


def test_booking_create_valid():
    now = datetime.now(UTC)
    later = now + timedelta(hours=1)
    b = BookingCreate(
        customer_name="Alice",
        customer_email="alice@example.com",
        starts_at=now,
        ends_at=later,
        notes="ok",
    )
    assert b.customer_email == "alice@example.com"


def test_booking_create_invalid_time_order():
    now = datetime.now(UTC)
    earlier = now - timedelta(minutes=10)
    with pytest.raises(ValidationError):
        BookingCreate(
            customer_name="Alice",
            customer_email="alice@example.com",
            starts_at=now,
            ends_at=earlier,
        )
