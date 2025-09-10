from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.booking import BookingCreate, BookingOut, BookingUpdate
from src.db.models.booking import Booking, BookingStatus
from src.db.session import get_db

router = APIRouter(prefix="/bookings", tags=["bookings"])


async def _get_booking_or_404(db: AsyncSession, booking_id: UUID) -> Booking:
    """Fetch a booking or raise 404. Keeps handlers small and consistent."""
    res = await db.execute(select(Booking).where(Booking.id == booking_id))
    obj = res.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return obj


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: BookingCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a booking. DB assigns timestamps; we default status to 'pending'."""
    obj = Booking(
        customer_email=payload.customer_email,
        start_time=payload.start_time,
        end_time=payload.end_time,
        status=BookingStatus.pending,
        notes=payload.notes,
    )
    db.add(obj)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(
    booking_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Read a single booking by id."""
    return await _get_booking_or_404(db, booking_id)


@router.get("", response_model=list[BookingOut])
async def list_bookings(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Annotated[int, Query(50, ge=1, le=200)] = 50,
    offset: Annotated[int, Query(0, ge=0)] = 0,
    email: Annotated[str | None, Query(None, description="Filter by customer email")] = None,
    status_: Annotated[
        BookingStatus | None,
        Query(None, alias="status", description="Filter by status"),
    ] = None,
):
    """List bookings with simple pagination and optional filters."""
    stmt = select(Booking).order_by(Booking.created_at.desc()).limit(limit).offset(offset)
    if email:
        stmt = stmt.where(Booking.customer_email == email)
    if status_:
        stmt = stmt.where(Booking.status == status_)
    result = await db.execute(stmt)
    return list(result.scalars())


@router.patch("/{booking_id}", response_model=BookingOut)
async def update_booking(
    booking_id: UUID,
    payload: BookingUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Partial update; only provided fields change. Returns the updated row."""
    obj = await _get_booking_or_404(db, booking_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.flush()
    await db.refresh(obj)
    return obj


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Delete a booking. Returns 204 on success."""
    _ = await _get_booking_or_404(db, booking_id)
    await db.delete(_)
    return None
