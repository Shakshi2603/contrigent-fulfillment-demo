from __future__ import annotations

from datetime import datetime

import pytest

from booking_demo import (
    BookingConflictError,
    InvalidReservationError,
    ReservationAlreadyExistsError,
)

from conftest import at


def test_create_and_get_reservation(service) -> None:
    created = service.create_reservation(
        "r-100", "Alex Kim", at(9), at(10), ["meeting-room-a"]
    )

    assert service.get_reservation("r-100") == created
    assert created.customer_name == "Alex Kim"


def test_create_reservation_with_multiple_resources(service) -> None:
    reservation = service.create_reservation(
        "r-101",
        "Taylor Singh",
        at(10),
        at(11),
        ["meeting-room-a", "projector-1", "camera-1"],
    )

    assert reservation.resource_ids == (
        "meeting-room-a",
        "projector-1",
        "camera-1",
    )


def test_create_normalizes_duplicate_resources(service, store) -> None:
    reservation = service.create_reservation(
        "r-102",
        "Chris Wong",
        at(11),
        at(12),
        ["projector-1", "projector-1", "camera-1"],
    )

    assert reservation.resource_ids == ("projector-1", "camera-1")
    assert store.allocation_snapshot()["projector-1"] == ("r-102",)


def test_create_rejects_obvious_overlap(service) -> None:
    service.create_reservation(
        "r-103", "Dana Brooks", at(10), at(11), ["meeting-room-a"]
    )

    with pytest.raises(BookingConflictError):
        service.create_reservation(
            "r-104", "Lee Park", at(10, 30), at(11, 30), ["meeting-room-a"]
        )


def test_create_allows_back_to_back_reservations(service) -> None:
    service.create_reservation(
        "r-105", "Jamie Fox", at(10), at(11), ["meeting-room-a"]
    )

    second = service.create_reservation(
        "r-106", "Robin Shah", at(11), at(12), ["meeting-room-a"]
    )

    assert second.reservation_id == "r-106"


def test_create_rejects_duplicate_reservation_id(service) -> None:
    service.create_reservation("r-107", "Pat Green", at(8), at(9), ["camera-1"])

    with pytest.raises(ReservationAlreadyExistsError):
        service.create_reservation(
            "r-107", "New Customer", at(12), at(13), ["camera-2"]
        )


def test_create_requires_timezone_aware_times(service) -> None:
    naive_start = datetime(2026, 8, 20, 9, 0)

    with pytest.raises(InvalidReservationError):
        service.create_reservation(
            "r-108", "Casey Hall", naive_start, at(10), ["meeting-room-a"]
        )


def test_create_rejects_invalid_time_range(service) -> None:
    with pytest.raises(InvalidReservationError):
        service.create_reservation(
            "r-109", "Mina Cole", at(10), at(10), ["meeting-room-a"]
        )


def test_create_requires_at_least_one_resource(service) -> None:
    with pytest.raises(InvalidReservationError):
        service.create_reservation("r-110", "Riley Stone", at(9), at(10), [])
