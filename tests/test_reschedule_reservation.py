from __future__ import annotations

import pytest

from booking_demo import BookingConflictError, InvalidReservationError, ReservationNotFoundError

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


def test_reschedule_rejects_conflicting_resource(service) -> None:
    service.create_reservation(
        "r-203", "Dana Brooks", at(9), at(10), ["meeting-room-a"]
    )
    service.create_reservation(
        "r-204", "Lee Park", at(11), at(12), ["projector-1"]
    )

    with pytest.raises(BookingConflictError):
        service.reschedule_reservation(
            "r-203", at(11, 15), at(11, 45), ["projector-1"]
        )


def test_reschedule_unknown_reservation_raises(service) -> None:
    with pytest.raises(ReservationNotFoundError):
        service.reschedule_reservation("missing", at(10), at(11))


def test_reschedule_rejects_invalid_time_range(service) -> None:
    service.create_reservation(
        "r-205", "Jamie Fox", at(9), at(10), ["meeting-room-a"]
    )

    with pytest.raises(InvalidReservationError):
        service.reschedule_reservation("r-205", at(12), at(11))
