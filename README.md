# Contrigent Booking Demo

A small Python shared-resource booking system for coworking-style reservations. A single reservation can hold several resources at the same time, such as a meeting room, projector, camera, or microphone.

The project intentionally stays lightweight: it uses an in-memory store, standard-library application code, and pytest for tests.

## Features

- Create a reservation for one or more resources
- Retrieve a reservation by ID
- List reservations in chronological order
- Reschedule an existing reservation
- Cancel a reservation and release its resources
- Detect overlapping resource bookings
- Require timezone-aware `datetime` values

Reservations use half-open time intervals: `[start, end)`. A booking ending at 11:00 can therefore be followed by another booking starting at 11:00.

## Project structure

```text
contrigent-booking-demo/
├── .gitignore
├── README.md
├── pyproject.toml
├── uv.lock
├── src/
│   └── booking_demo/
│       ├── __init__.py
│       ├── demo.py
│       ├── errors.py
│       ├── models.py
│       ├── service.py
│       └── store.py
└── tests/
    ├── conftest.py
    ├── test_cancel_reservation.py
    ├── test_create_reservation.py
    └── test_reschedule_reservation.py
```

## Requirements

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)

## Installation

From the repository root:

```bash
uv sync
```

`uv` will create the project environment and install the development dependencies from `uv.lock`.

## Run the tests

```bash
uv run python -m pytest -v
```

## Run the demo

```bash
uv run python -m booking_demo.demo
```

The demo creates several bookings, performs normal rescheduling and cancellation operations, and prints the in-memory booking state.

## Basic usage

```python
from datetime import datetime, timezone

from booking_demo import BookingService, InMemoryBookingStore

store = InMemoryBookingStore()
service = BookingService(store)

reservation = service.create_reservation(
    reservation_id="reservation-100",
    customer_name="Avery Chen",
    start_time=datetime(2026, 8, 20, 10, 0, tzinfo=timezone.utc),
    end_time=datetime(2026, 8, 20, 11, 0, tzinfo=timezone.utc),
    resource_ids=["meeting-room-a", "projector-1"],
)

updated = service.reschedule_reservation(
    reservation.reservation_id,
    start_time=datetime(2026, 8, 20, 11, 0, tzinfo=timezone.utc),
    end_time=datetime(2026, 8, 20, 12, 0, tzinfo=timezone.utc),
)

print(updated)
```
