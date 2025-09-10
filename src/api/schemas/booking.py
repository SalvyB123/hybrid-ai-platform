from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator


class BookingBase(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    customer_email: EmailStr
    starts_at: datetime
    ends_at: datetime
    notes: str | None = None

    # Pydantic v2 cross-field validation
    @model_validator(mode="after")
    def _check_times(self):
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    customer_name: str | None = None
    customer_email: EmailStr | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _check_times_if_both_present(self):
        # Only validate if both are provided in a partial update
        if self.starts_at is not None and self.ends_at is not None:
            if self.ends_at <= self.starts_at:
                raise ValueError("ends_at must be after starts_at")
        return self


class BookingOut(BookingBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2: ORM mode
