from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


# Shared fields for create and update
class BookingBase(BaseModel):
    customer_name: str = Field(min_length=1, max_length=120)
    customer_email: EmailStr
    starts_at: datetime
    ends_at: datetime
    notes: Optional[str] = None

    @field_validator("ends_at")
    @classmethod
    def ends_after_starts(cls, v: datetime, values: dict) -> datetime:
        starts = values.get("starts_at")
        if starts and v <= starts:
            raise ValueError("ends_at must be after starts_at")
        return v


# Create schema = all required
class BookingCreate(BookingBase):
    pass


# Update schema = all optional
class BookingUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[EmailStr] = None
    starts_at: Optional[datetime] = None
    ends_at: Optional[datetime] = None
    notes: Optional[str] = None


# Output schema = full DB record
class BookingOut(BookingBase):
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # ORM mode in Pydantic v2
