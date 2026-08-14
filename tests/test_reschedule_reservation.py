from __future__ import annotations

import pytest

from booking_demo import (
    BookingConflictError,
    InvalidReservationError,
    ReservationNotFoundError,
)

from conftest import at


def test_reschedule_changes_time(service) -> None:
    service.create_reservation(
        "r-200", "Alex Kim", at(9), at(10), ["meeting-room-a"]
    )

    updated = service.reschedule_reservation("r-200", at(10), at(11))

    assert updated.start_time == at(10)
    assert updated.end_time == at(11)
    assert updated.resource_ids == ("meeting-room-a",)


def test_reschedule_can_change_resources(service, store) -> None:
    service.create_reservation(
        "r-201", "Taylor Singh", at(9), at(10), ["meeting-room-a"]
    )

    updated = service.reschedule_reservation(
        "r-201", at(12), at(13), ["meeting-room-b", "projector-1"]
    )

    assert updated.resource_ids == ("meeting-room-b", "projector-1")
    assert "meeting-room-a" not in store.allocation_snapshot()


def test_successful_reschedule_keeps_reservation_identity(service) -> None:
    service.create_reservation("r-202", "Chris Wong", at(8), at(9), ["camera-1"])

    updated = service.reschedule_reservation(
        "r-202", at(14), at(15), ["camera-2"]
    )

    assert updated.reservation_id == "r-202"
    assert service.get_reservation("r-202") == updated


def test_reschedule_rollback_preserves_reservation_and_allocations(service, store) -> None:
    original = service.create_reservation(
        "r-203", "Dana Brooks", at(9), at(10), ["meeting-room-a", "projector-1"]
    )
    blocker = service.create_reservation(
        "r-204", "Lee Park", at(11), at(12), ["projector-1"]
    )

    before_reservation = service.get_reservation("r-203")
    before_snapshot = store.allocation_snapshot()

    with pytest.raises(BookingConflictError):
        service.reschedule_reservation(
            "r-203", at(11, 15), at(11, 45), ["projector-1"]
        )

    assert service.get_reservation("r-203") == before_reservation == original
    assert service.get_reservation("r-204") == blocker
    assert store.allocation_snapshot() == before_snapshot
    assert store.reservations_for_resource("meeting-room-a") == [original]
    assert store.reservations_for_resource("projector-1") == [original, blocker]


def test_reschedule_allows_back_to_back_booking(service, store) -> None:
    service.create_reservation(
        "r-205", "Jamie Fox", at(9), at(10), ["meeting-room-a"]
    )
    service.create_reservation(
        "r-206", "Robin Shah", at(10), at(11), ["meeting-room-a"]
    )

    updated = service.reschedule_reservation("r-205", at(8), at(10), ["meeting-room-a"])

    assert updated.start_time == at(8)
    assert updated.end_time == at(10)
    assert service.get_reservation("r-206").start_time == at(10)
    assert store.allocation_snapshot()["meeting-room-a"] == ("r-205", "r-206")


def test_create_allows_back_to_back_booking(service, store) -> None:
    first = service.create_reservation(
        "r-207", "Jamie Fox", at(9), at(10), ["meeting-room-a"]
    )

    second = service.create_reservation(
        "r-208", "Robin Shah", at(10), at(11), ["meeting-room-a"]
    )

    assert first.end_time == second.start_time
    assert store.allocation_snapshot()["meeting-room-a"] == ("r-207", "r-208")


def test_reschedule_back_to_back_booking_is_allowed(service, store) -> None:
    service.create_reservation(
        "r-209", "Jamie Fox", at(8), at(9), ["meeting-room-a"]
    )
    service.create_reservation(
        "r-210", "Robin Shah", at(10), at(11), ["meeting-room-a"]
    )

    updated = service.reschedule_reservation("r-209", at(9), at(10))

    assert updated.end_time == at(10)
    assert service.get_reservation("r-210").start_time == at(10)
    assert store.allocation_snapshot()["meeting-room-a"] == ("r-209", "r-210")


def test_reschedule_unknown_reservation_raises(service) -> None:
    with pytest.raises(ReservationNotFoundError):
        service.reschedule_reservation("missing", at(10), at(11))


def test_reschedule_rejects_invalid_time_range(service) -> None:
    service.create_reservation(
        "r-211", "Jamie Fox", at(9), at(10), ["meeting-room-a"]
    )

    with pytest.raises(InvalidReservationError):
        service.reschedule_reservation("r-211", at(12), at(11))
