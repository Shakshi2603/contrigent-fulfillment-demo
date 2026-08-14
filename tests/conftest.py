from __future__ import annotations

from datetime import datetime, timezone

import pytest

from booking_demo import BookingService, InMemoryBookingStore

UTC = timezone.utc


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 8, 20, hour, minute, tzinfo=UTC)


@pytest.fixture
def store() -> InMemoryBookingStore:
    return InMemoryBookingStore()


@pytest.fixture
def service(store: InMemoryBookingStore) -> BookingService:
    return BookingService(store)
