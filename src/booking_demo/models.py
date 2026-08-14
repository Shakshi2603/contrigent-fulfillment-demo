"""Domain models for the booking system."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Reservation:
    """A reservation that holds one or more shared resources for a time window."""

    reservation_id: str
    customer_name: str
    start_time: datetime
    end_time: datetime
    resource_ids: tuple[str, ...]
