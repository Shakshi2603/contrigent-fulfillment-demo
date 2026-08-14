from __future__ import annotations

import pytest

from booking_demo import ReservationNotFoundError

from conftest import at


def test_cancel_removes_reservation(service) -> None:
    service.create_reservation(
        "r-300", "Alex Kim", at(9), at(10), ["meeting-room-a"]
    )

    cancelled = service.cancel_reservation("r-300")

    assert cancelled.reservation_id == "r-300"
    with pytest.raises(ReservationNotFoundError):
        service.get_reservation("r-300")


def test_cancel_releases_resources_for_future_booking(service) -> None:
    service.create_reservation(
        "r-301", "Taylor Singh", at(10), at(11), ["projector-1"]
    )
    service.cancel_reservation("r-301")

    replacement = service.create_reservation(
        "r-302", "Chris Wong", at(10), at(11), ["projector-1"]
    )

    assert replacement.reservation_id == "r-302"


def test_cancel_unknown_reservation_raises(service) -> None:
    with pytest.raises(ReservationNotFoundError):
        service.cancel_reservation("missing")


def test_list_reservations_is_sorted_and_excludes_cancelled(service) -> None:
    service.create_reservation("r-304", "Late", at(13), at(14), ["camera-1"])
    service.create_reservation("r-303", "Early", at(9), at(10), ["camera-2"])
    service.create_reservation("r-305", "Middle", at(11), at(12), ["camera-3"])
    service.cancel_reservation("r-305")

    assert [item.reservation_id for item in service.list_reservations()] == [
        "r-303",
        "r-304",
    ]
