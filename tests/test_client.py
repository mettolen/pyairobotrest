"""Tests for Airobot thermostat client."""
# pylint: disable=redefined-outer-name,protected-access

import base64
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from pyairobotrest import AirobotClient
from pyairobotrest.exceptions import (
    AirobotAuthError,
    AirobotConnectionError,
    AirobotError,
    AirobotTimeoutError,
)
from pyairobotrest.models import ThermostatStatus


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = MagicMock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture
def client(mock_session):
    """Create a test client."""
    return AirobotClient(
        host="192.168.1.100",
        username="T01TEST123",
        password="test_password",
        session=mock_session,
    )


@pytest.fixture
def sample_thermostat_data():
    """Sample thermostat API response data."""
    return {
        "DEVICE_ID": "T01TEST123",
        "HW_VERSION": 256,
        "FW_VERSION": 262,
        "TEMP_AIR": 220,  # 22.0°C
        "HUM_AIR": 400,  # 40.0%
        "TEMP_FLOOR": 300,  # 30.0°C
        "CO2": 800,
        "AQI": 2,
        "DEVICE_UPTIME": 124,
        "HEATING_UPTIME": 117,
        "ERRORS": 0,
        "SETPOINT_TEMP": 245,  # 24.5°C
        "STATUS_FLAGS": [{"WINDOW_OPEN_DETECTED": 0, "HEATING_ON": 1}],
    }


def setup_mock_response(mock_session, response_data, status=200):
    """Helper to set up mock HTTP response."""
    mock_response = AsyncMock()
    mock_response.status = status
    mock_response.json = AsyncMock(return_value=response_data)

    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    mock_session.request = MagicMock(return_value=mock_context)
    return mock_response


@pytest.mark.asyncio
async def test_get_statuses(client, sample_thermostat_data):
    """Test getting thermostat status."""
    setup_mock_response(client._session, sample_thermostat_data)
    status = await client.get_statuses()

    assert isinstance(status, ThermostatStatus)
    assert status.device_id == "T01TEST123"
    assert status.hw_version == 256
    assert status.fw_version == 262
    assert status.temp_air == 22.0
    assert status.hum_air == 40.0
    assert status.temp_floor == 30.0
    assert status.co2 == 800
    assert status.aqi == 2
    assert status.setpoint_temp == 24.5
    assert status.is_heating is True
    assert status.has_error is False
    assert status.has_floor_sensor is True
    assert status.has_co2_sensor is True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "sensor_field,sensor_value,status_attr,has_sensor_attr",
    [
        ("TEMP_FLOOR", 32767, "temp_floor", "has_floor_sensor"),
        ("TEMP_AIR", 32767, "temp_air", None),
        (
            "HUM_AIR",
            65535,
            "hum_air",
            None,
        ),  # Uses UINT16 (65535) for unsigned percentage
        ("CO2", 65535, "co2", "has_co2_sensor"),
    ],
)
async def test_get_statuses_sensor_not_attached(
    client,
    sample_thermostat_data,
    sensor_field,
    sensor_value,
    status_attr,
    has_sensor_attr,
):
    """Test status parsing when various sensors are not attached."""
    sample_thermostat_data[sensor_field] = sensor_value
    if sensor_field == "CO2":
        sample_thermostat_data.pop("AQI", None)

    setup_mock_response(client._session, sample_thermostat_data)
    status = await client.get_statuses()

    assert getattr(status, status_attr) is None
    if has_sensor_attr:
        assert getattr(status, has_sensor_attr) is False
    if sensor_field == "CO2":
        assert status.aqi is None


@pytest.mark.asyncio
async def test_auth_error(client):
    """Test authentication error handling."""

    # Mock the _request method to raise AirobotAuthError directly
    async def mock_request(*args, **kwargs):
        raise AirobotAuthError("Authentication failed - check username/password")

    client._request = mock_request

    with pytest.raises(AirobotAuthError):
        await client.get_statuses()


@pytest.mark.asyncio
async def test_connection_error(client):
    """Test connection error handling."""
    client._session.request = MagicMock(
        side_effect=aiohttp.ClientError("Connection failed")
    )

    with pytest.raises(AirobotConnectionError):
        await client.get_statuses()


@pytest.mark.asyncio
async def test_timeout_error(client):
    """Test timeout error handling."""
    # Mock TimeoutError to be raised during request
    client._session.request = MagicMock(side_effect=TimeoutError("Request timeout"))

    client._timeout = 0.1  # Set a short timeout

    with pytest.raises(AirobotTimeoutError):
        await client.get_statuses()


@pytest.mark.asyncio
async def test_context_manager():
    """Test client as context manager."""
    async with AirobotClient(
        host="192.168.1.100", username="T01TEST123", password="test_password"
    ) as client:
        assert client is not None
        assert client.username == "T01TEST123"
    # Session should be closed after exiting context


@pytest.mark.asyncio
async def test_auth_header_creation():
    """Test Basic Auth header creation."""
    client = AirobotClient(
        host="192.168.1.100", username="T01TEST123", password="test_password"
    )

    # The auth header should be Base64 encoded "username:password"
    assert client._auth_header.startswith("Basic ")

    # Decode and verify
    encoded_part = client._auth_header.split(" ")[1]
    decoded = base64.b64decode(encoded_part).decode()
    assert decoded == "T01TEST123:test_password"


def test_url_building():
    """Test URL building for API endpoints."""
    client = AirobotClient(
        host="192.168.1.100", username="T01TEST123", password="test_password"
    )

    url = client._build_url("/getStatuses")
    assert url == "http://192.168.1.100:80/api/thermostat/getStatuses"


@pytest.mark.asyncio
async def test_validation_warnings(client, caplog):
    """Test validation warnings for out-of-range values."""
    # Data with out-of-range values
    invalid_data = {
        "DEVICE_ID": "T01TEST123",
        "HW_VERSION": 100,  # Below min (256)
        "FW_VERSION": 1000,  # Above max (999)
        "TEMP_AIR": -10000,  # Way below min
        "HUM_AIR": 70000,  # Way above max
        "TEMP_FLOOR": 300,
        "CO2": 800,
        "AQI": 10,  # Above max (5)
        "DEVICE_UPTIME": 124,
        "HEATING_UPTIME": 117,
        "ERRORS": 0,
        "SETPOINT_TEMP": 10,  # Below min (50 in raw units = 5.0°C)
        "STATUS_FLAGS": [{"WINDOW_OPEN_DETECTED": 0, "HEATING_ON": 1}],
    }

    setup_mock_response(client._session, invalid_data)

    # Capture logs
    with caplog.at_level("WARNING"):
        status = await client.get_statuses()

    # Verify the object is still created
    assert isinstance(status, ThermostatStatus)
    assert status.device_id == "T01TEST123"

    # Verify warnings were logged
    warning_messages = [
        record.message for record in caplog.records if record.levelname == "WARNING"
    ]

    # Check that we got warnings for the out-of-range values
    assert any("HW_VERSION" in msg and "100" in msg for msg in warning_messages)
    assert any("FW_VERSION" in msg and "1000" in msg for msg in warning_messages)
    assert any("AQI" in msg and "10" in msg for msg in warning_messages)


@pytest.mark.asyncio
async def test_string_values_conversion(mock_session):
    """Test that string numeric values are properly converted to integers."""
    # Mock response with string numeric values (as returned by real API)
    mock_data = {
        "HW_VERSION": "257",  # String instead of int
        "FW_VERSION": "265",  # String instead of int
        "TEMP_AIR": 245,
        "HUM_AIR": 322,
        "TEMP_FLOOR": 32767,  # Sensor not attached
        "CO2": 1110,
        "AQI": 3,
        "SETPOINT_TEMP": 240,
        "DEVICE_UPTIME": "657827",  # String instead of int
        "HEATING_UPTIME": "104954",  # String instead of int
        "ERRORS": "0",  # String instead of int
        "STATUS_FLAGS": [{"WINDOW_OPEN_DETECTED": 0, "HEATING_ON": 0}],
    }

    setup_mock_response(mock_session, mock_data)

    client = AirobotClient("192.168.1.100", "test_user", "test_pass")
    client._session = mock_session

    status = await client.get_statuses()

    # Verify that string values were properly converted
    assert isinstance(status.hw_version, int)
    assert status.hw_version == 257
    assert isinstance(status.fw_version, int)
    assert status.fw_version == 265
    assert isinstance(status.device_uptime, int)
    assert status.device_uptime == 657827
    assert isinstance(status.heating_uptime, int)
    assert status.heating_uptime == 104954
    assert isinstance(status.errors, int)
    assert status.errors == 0


@pytest.mark.asyncio
async def test_session_creation_and_closing():
    """Test automatic session creation and cleanup."""
    # Create client without providing session
    client = AirobotClient("192.168.1.100", "test_user", "test_pass")

    # Initially no session
    assert client._session is None

    # Getting session should create one
    session = await client._get_session()
    assert session is not None
    assert client._session is session
    assert client._close_session is True  # Should mark for closing

    # Getting session again should return the same one
    session2 = await client._get_session()
    assert session2 is session

    # Close should clean up the session
    await client.close()
    assert client._session is None


@pytest.mark.asyncio
async def test_session_provided_externally():
    """Test behavior when session is provided externally."""
    external_session = MagicMock(spec=aiohttp.ClientSession)
    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=external_session
    )

    # Should use provided session
    session = await client._get_session()
    assert session is external_session
    assert client._close_session is False  # Should NOT mark for closing

    # Close should not close external session
    await client.close()
    assert client._session is external_session  # Still there


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_code,exception_type,expected_message",
    [
        (401, AirobotAuthError, "Authentication failed - check username/password"),
        (403, AirobotAuthError, "Access forbidden"),
        (500, AirobotError, "API request failed with status 500"),
    ],
)
async def test_http_errors(status_code, exception_type, expected_message):
    """Test HTTP error handling for various status codes."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=mock_session
    )

    setup_mock_response(mock_session, {}, status=status_code)

    with pytest.raises(exception_type) as exc_info:
        await client._request("GET", "/test")

    assert expected_message in str(exc_info.value)
