from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_list_read_update_delete_booking(test_client: AsyncClient):
    # Create
    now = datetime.now(timezone.utc).replace(microsecond=0)
    later = now + timedelta(hours=1)
    payload = {
        "customer_name": "Alice",
        "customer_email": "alice@example.com",
        "starts_at": now.isoformat(),
        "ends_at": later.isoformat(),
        "notes": "Demo",
    }
    r = await test_client.post("/bookings", json=payload)
    assert r.status_code == 201, r.text
    created = r.json()
    bid = created["id"]

    # List
    r = await test_client.get("/bookings?limit=10")
    assert r.status_code == 200
    assert any(item["id"] == bid for item in r.json())

    # Read
    r = await test_client.get(f"/bookings/{bid}")
    assert r.status_code == 200
    assert r.json()["customer_email"] == "alice@example.com"

    # Update
    r = await test_client.patch(f"/bookings/{bid}", json={"notes": "Updated"})
    assert r.status_code == 200
    assert r.json()["notes"] == "Updated"

    # Delete
    r = await test_client.delete(f"/bookings/{bid}")
    assert r.status_code == 204

    # Verify 404 after delete
    r = await test_client.get(f"/bookings/{bid}")
    assert r.status_code == 404
