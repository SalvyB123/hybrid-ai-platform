from __future__ import annotations

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.booking import BookingCreate, BookingUpdate, BookingOut
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
async def create_booking(payload: BookingCreate, db: AsyncSession = Depends(get_db)):
    """Create a booking. DB assigns timestamps; we default status to 'pending'."""
    obj = Booking(
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        starts_at=payload.starts_at,
        ends_at=payload.ends_at,
        notes=payload.notes,
        status=BookingStatus.pending,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)  # reload DB-assigned fields
    return obj


@router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    """Read a single booking by id."""
    return await _get_booking_or_404(db, booking_id)


@router.get("", response_model=list[BookingOut])
async def list_bookings(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    email: Optional[str] = Query(None, description="Filter by customer email"),
    status_: Optional[BookingStatus] = Query(None, alias="status", description="Filter by status"),
):
    """List bookings with simple pagination and optional filters."""
    stmt = select(Booking)
    if email:
        stmt = stmt.where(Booking.customer_email == email)
    if status_:
        stmt = stmt.where(Booking.status == status_)
    stmt = stmt.order_by(Booking.starts_at.desc()).limit(limit).offset(offset)
    res = await db.execute(stmt)
    return list(res.scalars().all())


@router.patch("/{booking_id}", response_model=BookingOut)
async def update_booking(booking_id: UUID, payload: BookingUpdate, db: AsyncSession = Depends(get_db)):
    """Partial update; only provided fields change. Returns the updated row."""
    _ = await _get_booking_or_404(db, booking_id)  # ensure it exists

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        res = await db.execute(select(Booking).where(Booking.id == booking_id))
        return res.scalar_one()

    if "starts_at" in updates and "ends_at" in updates:
        if updates["ends_at"] <= updates["starts_at"]:
            raise HTTPException(status_code=400, detail="ends_at must be after starts_at")

    stmt = (
        update(Booking)
        .where(Booking.id == booking_id)
        .values(**updates)
        .execution_options(synchronize_session="fetch")
        .returning(Booking)
    )
    res = await db.execute(stmt)
    await db.commit()
    return res.scalar_one()


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(booking_id: UUID, db: AsyncSession = Depends(get_db)):
    """Delete a booking. Returns 204 on success."""
    _ = await _get_booking_or_404(db, booking_id)
    await db.execute(delete(Booking).where(Booking.id == booking_id))
    await db.commit()
    return None
