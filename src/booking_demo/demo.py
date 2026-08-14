"""Command-line demonstration of the booking service."""

from __future__ import annotations

from datetime import datetime, timezone

from .errors import BookingConflictError
from .service import BookingService
from .store import InMemoryBookingStore

UTC = timezone.utc


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 8, 20, hour, minute, tzinfo=UTC)


def print_state(service: BookingService, store: InMemoryBookingStore) -> None:
    print("Reservations:")
    for reservation in service.list_reservations():
        resources = ", ".join(reservation.resource_ids)
        print(
            f"  {reservation.reservation_id}: {reservation.customer_name} | "
            f"{reservation.start_time:%H:%M}-{reservation.end_time:%H:%M} | "
            f"{resources}"
        )
    print("Allocations:")
    for resource_id, reservation_ids in store.allocation_snapshot().items():
        print(f"  {resource_id}: {', '.join(reservation_ids)}")


def main() -> None:
    store = InMemoryBookingStore()
    service = BookingService(store)

    service.create_reservation(
        "reservation-100",
        "Avery Chen",
        at(10),
        at(11),
        ["meeting-room-a", "projector-1"],
    )
    service.create_reservation(
        "reservation-200",
        "Morgan Lee",
        at(11),
        at(12),
        ["camera-1"],
    )
    service.create_reservation(
        "reservation-300",
        "Sam Rivera",
        at(9),
        at(10),
        ["meeting-room-c"],
    )
    service.create_reservation(
        "reservation-400",
        "Jordan Patel",
        at(13),
        at(14),
        ["microphone-1"],
    )

    print("=== Initial state ===")
    print_state(service, store)

    service.reschedule_reservation(
        "reservation-300",
        at(10),
        at(10, 30),
        ["meeting-room-c"],
    )
    service.cancel_reservation("reservation-400")

    print("\n=== After ordinary successful operations ===")
    print_state(service, store)

    print("\nAttempting a conflicting multi-resource reschedule...")
    try:
        service.reschedule_reservation(
            "reservation-100",
            at(11, 15),
            at(11, 45),
            ["meeting-room-b", "camera-1"],
        )
    except BookingConflictError as exc:
        print(f"Reschedule rejected: {exc}")

    print("\n=== State after failed reschedule ===")
    print_state(service, store)


if __name__ == "__main__":
    main()
