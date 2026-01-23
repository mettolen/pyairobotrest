"""Shared pytest fixtures for pyairobotrest tests."""
# pylint: disable=redefined-outer-name

from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from pyairobotrest import AirobotClient


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session.

    Returns:
        MagicMock: Mock session object that can be configured for different
            test scenarios.
    """
    session = MagicMock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture
def mock_session_with_response():
    """Create a mock aiohttp session with a standard 200 OK response.

    Returns:
        MagicMock: Mock session with pre-configured successful response.
    """
    session = MagicMock()
    response = AsyncMock()
    response.status = 200
    response.json.return_value = {}
    response.headers = {"Content-Type": "application/json"}
    session.request.return_value.__aenter__.return_value = response
    return session


@pytest.fixture
def client(mock_session):
    """Create a basic test client with mocked session.

    Args:
        mock_session: Mocked aiohttp session fixture.

    Returns:
        AirobotClient: Test client instance.
    """
    return AirobotClient(
        host="192.168.1.100",
        username="T01TEST123",
        password="test_password",
        session=mock_session,
    )


@pytest.fixture
def validation_client():
    """Create test client for validation tests (no mocked session).

    Returns:
        AirobotClient: Client instance for validation testing.
    """
    return AirobotClient(
        host="192.168.1.100",
        username="T01TEST123",
        password="test_password",
    )


@pytest.fixture
def sample_thermostat_data():
    """Sample thermostat status API response data.

    Returns:
        dict: Complete thermostat status data with all sensors.
    """
    return {
        "DEVICE_ID": "T01TEST123",
        "HW_VERSION": 256,
        "FW_VERSION": 262,
        "TEMP_AIR": 220,
        "HUM_AIR": 400,
        "TEMP_FLOOR": 300,
        "CO2": 800,
        "AQI": 2,
        "DEVICE_UPTIME": 124,
        "HEATING_UPTIME": 117,
        "ERRORS": 0,
        "SETPOINT_TEMP": 245,
        "STATUS_FLAGS": [{"WINDOW_OPEN_DETECTED": 0, "HEATING_ON": 1}],
    }


@pytest.fixture
def sample_thermostat_settings():
    """Sample thermostat settings API response data.

    Returns:
        dict: Complete thermostat settings data.
    """
    return {
        "DEVICE_ID": "T01TEST123",
        "MODE": 1,
        "SETPOINT_TEMP": 220,
        "SETPOINT_TEMP_AWAY": 180,
        "HYSTERESIS_BAND": 1,
        "DEVICE_NAME": "Test Thermostat",
        "SETTING_FLAGS": [
            {
                "REBOOT": 0,
                "ACTUATOR_EXERCISE_DISABLED": 0,
                "RECALIBRATE_CO2": 0,
                "CHILDLOCK_ENABLED": 0,
                "BOOST_ENABLED": 0,
            }
        ],
    }


def setup_mock_response(session, response_data, status=200):
    """Helper to set up mock HTTP response.

    Args:
        session: Mock session object to configure.
        response_data: Data to return from the mocked response.
        status: HTTP status code (default: 200).

    Returns:
        AsyncMock: Configured mock response object.
    """
    mock_response = AsyncMock()
    mock_response.status = status
    mock_response.json = AsyncMock(return_value=response_data)
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)
    session.request = MagicMock(return_value=mock_context)
    return mock_response
