"""Exceptions for pyairobotrest."""

__all__ = [
    "AirobotError",
    "AirobotConnectionError",
    "AirobotAuthError",
    "AirobotTimeoutError",
]


class AirobotError(Exception):
    """Base exception for Airobot errors."""


class AirobotConnectionError(AirobotError):
    """Exception raised when connection to Airobot device fails."""


class AirobotAuthError(AirobotError):
    """Exception raised when authentication fails."""


class AirobotTimeoutError(AirobotError):
    """Exception raised when request times out."""
