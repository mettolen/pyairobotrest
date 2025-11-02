"""Tests for custom exceptions."""

from pyairobotrest.exceptions import (
    AirobotAuthError,
    AirobotConnectionError,
    AirobotError,
    AirobotTimeoutError,
)


def test_base_exception():
    """Test base exception."""
    error = AirobotError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_connection_error():
    """Test connection error."""
    error = AirobotConnectionError("Connection failed")
    assert str(error) == "Connection failed"
    assert isinstance(error, AirobotError)


def test_auth_error():
    """Test authentication error."""
    error = AirobotAuthError("Authentication failed")
    assert str(error) == "Authentication failed"
    assert isinstance(error, AirobotError)


def test_timeout_error():
    """Test timeout error."""
    error = AirobotTimeoutError("Request timed out")
    assert str(error) == "Request timed out"
    assert isinstance(error, AirobotError)
