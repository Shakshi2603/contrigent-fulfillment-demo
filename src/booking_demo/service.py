"""Application service for creating and managing reservations."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from datetime import datetime

from .errors import (
    BookingConflictError,
    InvalidReservationError,
    ReservationAlreadyExistsError,
    ReservationNotFoundError,
)
from .models import Reservation
from .store import InMemoryBookingStore


class BookingService:
    """Coordinate booking validation, conflict checks, and persistence."""

    def __init__(self, store: InMemoryBookingStore) -> None:
        self._store = store

    def create_reservation(
        self,
        reservation_id: str,
        customer_name: str,
        start_time: datetime,
        end_time: datetime,
        resource_ids: Iterable[str],
    ) -> Reservation:
        self._validate_identity(reservation_id, customer_name)
        self._validate_time_range(start_time, end_time)
        normalized_resources = self._normalize_resource_ids(resource_ids)

        if self._store.get_reservation(reservation_id) is not None:
            raise ReservationAlreadyExistsError(
                f"Reservation '{reservation_id}' already exists."
            )

        for resource_id in normalized_resources:
            self._ensure_resource_available(resource_id, start_time, end_time)

        reservation = Reservation(
            reservation_id=reservation_id,
            customer_name=customer_name,
            start_time=start_time,
            end_time=end_time,
            resource_ids=normalized_resources,
        )
        self._store.save_reservation(reservation)
        self._store.allocate_many(normalized_resources, reservation_id)
        return reservation

    def get_reservation(self, reservation_id: str) -> Reservation:
        reservation = self._store.get_reservation(reservation_id)
        if reservation is None:
            raise ReservationNotFoundError(
                f"Reservation '{reservation_id}' was not found."
            )
        return reservation

    def list_reservations(self) -> list[Reservation]:
        return self._store.list_reservations()

    def reschedule_reservation(
        self,
        reservation_id: str,
        start_time: datetime,
        end_time: datetime,
        resource_ids: Iterable[str] | None = None,
    ) -> Reservation:
        current = self.get_reservation(reservation_id)
        self._validate_time_range(start_time, end_time)

        requested_resources = (
            current.resource_ids
            if resource_ids is None
            else self._normalize_resource_ids(resource_ids)
        )

        for resource_id in requested_resources:
            self._ensure_resource_available_for_reschedule(
                resource_id,
                start_time,
                end_time,
                reservation_id,
            )

        updated = replace(
            current,
            start_time=start_time,
            end_time=end_time,
            resource_ids=requested_resources,
        )

        self._store.save_reservation(updated)

        if requested_resources != current.resource_ids:
            self._store.release_reservation(reservation_id)
            self._store.allocate_many(requested_resources, reservation_id)

        return updated

    def cancel_reservation(self, reservation_id: str) -> Reservation:
        reservation = self.get_reservation(reservation_id)
        self._store.release_reservation(reservation_id)
        self._store.delete_reservation(reservation_id)
        return reservation

    @staticmethod
    def _validate_identity(reservation_id: str, customer_name: str) -> None:
        if not reservation_id.strip():
            raise InvalidReservationError("Reservation ID is required.")
        if not customer_name.strip():
            raise InvalidReservationError("Customer name is required.")

    @staticmethod
    def _validate_time_range(start_time: datetime, end_time: datetime) -> None:
        if start_time.tzinfo is None or start_time.utcoffset() is None:
            raise InvalidReservationError("Start time must be timezone-aware.")
        if end_time.tzinfo is None or end_time.utcoffset() is None:
            raise InvalidReservationError("End time must be timezone-aware.")
        if end_time <= start_time:
            raise InvalidReservationError("End time must be after start time.")

    @staticmethod
    def _normalize_resource_ids(resource_ids: Iterable[str]) -> tuple[str, ...]:
        normalized: list[str] = []
        seen: set[str] = set()
        for resource_id in resource_ids:
            resource_id = resource_id.strip()
            if not resource_id:
                raise InvalidReservationError("Resource IDs cannot be empty.")
            if resource_id not in seen:
                normalized.append(resource_id)
                seen.add(resource_id)
        if not normalized:
            raise InvalidReservationError("At least one resource ID is required.")
        return tuple(normalized)

    def _ensure_resource_available(
        self,
        resource_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> None:
        for existing in self._store.reservations_for_resource(resource_id):
            if self._overlaps(
                start_time,
                end_time,
                existing.start_time,
                existing.end_time,
            ):
                raise BookingConflictError(
                    f"Resource '{resource_id}' is already booked by "
                    f"'{existing.reservation_id}'."
                )

    def _ensure_resource_available_for_reschedule(
        self,
        resource_id: str,
        start_time: datetime,
        end_time: datetime,
        reservation_id: str,
    ) -> None:
        for existing in self._store.reservations_for_resource(resource_id):
            if existing.reservation_id == reservation_id:
                continue
            if self._overlaps(start_time, end_time, existing.start_time, existing.end_time):
                raise BookingConflictError(
                    f"Resource '{resource_id}' is already booked by "
                    f"'{existing.reservation_id}'."
                )

    @staticmethod
    def _overlaps(
        first_start: datetime,
        first_end: datetime,
        second_start: datetime,
        second_end: datetime,
    ) -> bool:
        return first_start < second_end and second_start < first_end
