# src/api/routes/health.py
from __future__ import annotations

import asyncio
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Adjust this import to your project layout:
from src.db.session import get_async_session  # async dependency

router = APIRouter(tags=["ops"])

class ProbeResponse(BaseModel):
    status: str  # "ok" | "degraded" | "error"
    details: dict | None = None

@router.get("/health", response_model=ProbeResponse, summary="Liveness probe")
async def health() -> ProbeResponse:
    """
    Liveness: cheap & fast. If the app can serve requests and event loop is alive, return ok.
    Avoid external calls here.
    """
    return ProbeResponse(status="ok")

@router.get("/readiness", response_model=ProbeResponse, summary="Readiness probe")
async def readiness(
    session: AsyncSession = Depends(get_async_session),
) -> ProbeResponse:
    """
    Readiness: verify critical downstreams (DB) within a tight timeout.
    Return non-200 to signal orchestrator to stop sending traffic.
    """
    async def check_db() -> dict:
        try:
            await session.execute(text("SELECT 1"))
            return {"db": "ok"}
        except Exception as exc:  # pragma: no cover (asserted via response)
            return {"db": f"error: {exc.__class__.__name__}"}

    # Keep the timeout small so the probe is responsive under failure
    try:
        details = await asyncio.wait_for(check_db(), timeout=1.5)
    except asyncio.TimeoutError:
        return ProbeResponse(status="error", details={"db": "timeout"})

    status = "ok" if details.get("db") == "ok" else "error"
    return ProbeResponse(status=status, details=details if status != "ok" else None)