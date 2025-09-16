# src/api/routes/health.py
from __future__ import annotations

import asyncio
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session

router = APIRouter(tags=["ops"])


class ProbeResponse(BaseModel):
    status: str  # "ok" | "error"
    details: dict | None = None


@router.get("/health", response_model=ProbeResponse, summary="Liveness probe")
async def health() -> ProbeResponse:
    """Cheap & fast liveness check."""
    return ProbeResponse(status="ok")


@router.get("/readiness", response_model=ProbeResponse, summary="Readiness probe")
async def readiness(
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> ProbeResponse:
    """
    Readiness: verify critical downstreams (DB) within a tight timeout.
    Returns JSON status; your orchestrator should read `status`.
    """

    async def check_db() -> dict:
        try:
            await session.execute(text("SELECT 1"))
            return {"db": "ok"}
        except Exception as exc:
            return {"db": f"error: {exc.__class__.__name__}"}

    try:
        details = await asyncio.wait_for(check_db(), timeout=1.5)
    except TimeoutError:  # asyncio.TimeoutError is deprecated alias
        return ProbeResponse(status="error", details={"db": "timeout"})

    status = "ok" if details.get("db") == "ok" else "error"
    return ProbeResponse(status=status, details=None if status == "ok" else details)
