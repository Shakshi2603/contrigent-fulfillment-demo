"""Exceptions raised by the booking domain."""


class BookingError(Exception):
    """Base class for booking-related errors."""


class InvalidReservationError(BookingError):
    """Raised when reservation input is invalid."""


class ReservationNotFoundError(BookingError):
    """Raised when a reservation ID does not exist."""


class ReservationAlreadyExistsError(BookingError):
    """Raised when a reservation ID is already in use."""


class BookingConflictError(BookingError):
    """Raised when a required resource is already booked."""
