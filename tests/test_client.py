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


@pytest.mark.asyncio
async def test_get_statuses(client, sample_thermostat_data):
    """Test getting thermostat status."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=sample_thermostat_data)

    client._session.request = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock()
        )
    )

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
async def test_get_statuses_no_floor_sensor(
    client, mock_session, sample_thermostat_data
):
    """Test status parsing when floor sensor is not attached."""
    sample_thermostat_data["TEMP_FLOOR"] = 32767  # Indicates no sensor

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=sample_thermostat_data)

    mock_session.request = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock()
        )
    )

    status = await client.get_statuses()

    assert status.temp_floor is None
    assert status.has_floor_sensor is False


@pytest.mark.asyncio
async def test_get_statuses_no_co2_sensor(client, sample_thermostat_data):
    """Test status parsing when CO2 sensor is not equipped."""
    sample_thermostat_data["CO2"] = 65535  # Indicates no sensor
    sample_thermostat_data.pop("AQI", None)  # AQI not available without CO2 sensor

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=sample_thermostat_data)

    client._session.request = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock()
        )
    )

    status = await client.get_statuses()

    assert status.co2 is None
    assert status.aqi is None
    assert status.has_co2_sensor is False


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

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=invalid_data)

    client._session.request = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock()
        )
    )

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
        "TEMP_FLOOR": 32767,
        "CO2": 1110,
        "AQI": 3,
        "SETPOINT_TEMP": 240,
        "DEVICE_UPTIME": "657827",  # String instead of int
        "HEATING_UPTIME": "104954",  # String instead of int
        "ERRORS": "0",  # String instead of int
        "STATUS_FLAGS": [{"WINDOW_OPEN_DETECTED": 0, "HEATING_ON": 0}],
    }

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value=mock_data)

    mock_session.request = MagicMock(
        return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response), __aexit__=AsyncMock()
        )
    )

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
async def test_http_403_error():
    """Test 403 Forbidden error handling."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=mock_session
    )

    mock_response = AsyncMock()
    mock_response.status = 403
    mock_response.json = AsyncMock(return_value={})

    # Create a proper async context manager mock
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    mock_session.request = MagicMock(return_value=mock_context)

    with pytest.raises(AirobotAuthError) as exc_info:
        await client._request("GET", "/test")

    assert "Access forbidden" in str(exc_info.value)
    assert "Local API" in str(exc_info.value)


@pytest.mark.asyncio
async def test_http_401_error():
    """Test 401 Unauthorized error handling."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=mock_session
    )

    mock_response = AsyncMock()
    mock_response.status = 401
    mock_response.json = AsyncMock(return_value={})

    # Create a proper async context manager mock
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    mock_session.request = MagicMock(return_value=mock_context)

    with pytest.raises(AirobotAuthError) as exc_info:
        await client._request("GET", "/test")

    assert "Authentication failed - check username/password" in str(exc_info.value)


@pytest.mark.asyncio
async def test_http_generic_error():
    """Test generic HTTP error handling (4xx/5xx status codes)."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=mock_session
    )

    mock_response = AsyncMock()
    mock_response.status = 500
    mock_response.json = AsyncMock(return_value={})

    # Create a proper async context manager mock
    mock_context = AsyncMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    mock_session.request = MagicMock(return_value=mock_context)

    with pytest.raises(AirobotError) as exc_info:
        await client._request("GET", "/test")

    assert "API request failed with status 500" in str(exc_info.value)
