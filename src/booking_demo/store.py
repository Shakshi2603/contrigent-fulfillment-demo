"""In-memory persistence for reservations and resource allocations."""

from __future__ import annotations

from collections.abc import Iterable

from .models import Reservation


class InMemoryBookingStore:
    """Store reservation records and the resources allocated to them."""

    def __init__(self) -> None:
        self._reservations: dict[str, Reservation] = {}
        self._allocations: dict[str, list[str]] = {}

    def save_reservation(self, reservation: Reservation) -> None:
        self._reservations[reservation.reservation_id] = reservation

    def get_reservation(self, reservation_id: str) -> Reservation | None:
        return self._reservations.get(reservation_id)

    def delete_reservation(self, reservation_id: str) -> None:
        self._reservations.pop(reservation_id, None)

    def list_reservations(self) -> list[Reservation]:
        return sorted(
            self._reservations.values(),
            key=lambda reservation: (reservation.start_time, reservation.reservation_id),
        )

    def allocate(self, resource_id: str, reservation_id: str) -> None:
        self._allocations.setdefault(resource_id, []).append(reservation_id)

    def allocate_many(self, resource_ids: Iterable[str], reservation_id: str) -> None:
        for resource_id in resource_ids:
            self.allocate(resource_id, reservation_id)

    def release_reservation(self, reservation_id: str) -> None:
        empty_resources: list[str] = []
        for resource_id, reservation_ids in self._allocations.items():
            self._allocations[resource_id] = [
                item for item in reservation_ids if item != reservation_id
            ]
            if not self._allocations[resource_id]:
                empty_resources.append(resource_id)

        for resource_id in empty_resources:
            del self._allocations[resource_id]

    def reservations_for_resource(self, resource_id: str) -> list[Reservation]:
        reservations: list[Reservation] = []
        for reservation_id in self._allocations.get(resource_id, []):
            reservation = self._reservations.get(reservation_id)
            if reservation is not None:
                reservations.append(reservation)
        return reservations

    def allocation_snapshot(self) -> dict[str, tuple[str, ...]]:
        """Return an immutable-by-value view useful for diagnostics and demos."""
        return {
            resource_id: tuple(reservation_ids)
            for resource_id, reservation_ids in sorted(self._allocations.items())
        }
