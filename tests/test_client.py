"""Tests for Airobot thermostat client."""
# pylint: disable=redefined-outer-name,protected-access

import base64
from typing import Any
from unittest.mock import MagicMock

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

from .conftest import setup_mock_response


@pytest.mark.asyncio
async def test_get_statuses(
    client: AirobotClient, sample_thermostat_data: dict[str, Any]
) -> None:
    """Test getting thermostat status with all sensor data."""
    setup_mock_response(client._session, sample_thermostat_data)
    status = await client.get_statuses()

    assert isinstance(status, ThermostatStatus)
    assert status.device_id == "T01TEST123"
    assert status.hw_version == 256
    assert status.fw_version == 262
    assert status.hw_version_string == "1.0"
    assert status.fw_version_string == "1.6"
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
        ("HUM_AIR", 65535, "hum_air", None),
        ("CO2", 65535, "co2", "has_co2_sensor"),
    ],
)
async def test_sensor_not_attached(
    client: AirobotClient,
    sample_thermostat_data: dict[str, Any],
    sensor_field: str,
    sensor_value: int,
    status_attr: str,
    has_sensor_attr: str | None,
) -> None:
    """Test status parsing when sensors are not attached."""
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
@pytest.mark.parametrize(
    "status_code,exception_type,expected_message",
    [
        (401, AirobotAuthError, "Authentication failed - check username/password"),
        (403, AirobotAuthError, "Access forbidden"),
        (500, AirobotError, "API request failed with status 500"),
    ],
)
async def test_http_errors(
    status_code: int, exception_type: type, expected_message: str
) -> None:
    """Test HTTP error handling for various status codes."""
    mock_session = MagicMock(spec=aiohttp.ClientSession)
    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=mock_session
    )
    setup_mock_response(mock_session, {}, status=status_code)

    with pytest.raises(exception_type, match=expected_message):
        await client._request("GET", "/test")


@pytest.mark.asyncio
async def test_connection_error(client: AirobotClient) -> None:
    """Test connection error handling."""
    client._session.request = MagicMock(  # type: ignore[union-attr, method-assign]
        side_effect=aiohttp.ClientError("Connection failed")
    )

    with pytest.raises(AirobotConnectionError):
        await client.get_statuses()


@pytest.mark.asyncio
async def test_timeout_error(client: AirobotClient) -> None:
    """Test timeout error handling."""
    client._session.request = MagicMock(side_effect=TimeoutError("Request timeout"))  # type: ignore[union-attr, method-assign]
    client._timeout = 1  # Change to int to match type hint

    with pytest.raises(AirobotTimeoutError):
        await client.get_statuses()


@pytest.mark.asyncio
async def test_context_manager() -> None:
    """Test client as context manager."""
    async with AirobotClient(
        host="192.168.1.100", username="T01TEST123", password="test_password"
    ) as client:
        assert client is not None
        assert client.username == "T01TEST123"


@pytest.mark.asyncio
async def test_auth_header_creation() -> None:
    """Test Basic Auth header creation."""
    client = AirobotClient(
        host="192.168.1.100", username="T01TEST123", password="test_password"
    )
    assert client._auth_header.startswith("Basic ")
    encoded_part = client._auth_header.split(" ")[1]
    decoded = base64.b64decode(encoded_part).decode()
    assert decoded == "T01TEST123:test_password"


def test_url_building() -> None:
    """Test URL building for API endpoints."""
    client = AirobotClient(
        host="192.168.1.100", username="T01TEST123", password="test_password"
    )
    url = client._build_url("/getStatuses")
    assert url == "http://192.168.1.100:80/api/thermostat/getStatuses"


@pytest.mark.asyncio
async def test_string_values_conversion(mock_session: MagicMock) -> None:
    """Test that string numeric values are properly converted."""
    mock_data = {
        "HW_VERSION": "257",
        "FW_VERSION": "265",
        "TEMP_AIR": 245,
        "HUM_AIR": 322,
        "TEMP_FLOOR": 32767,
        "CO2": 1110,
        "AQI": 3,
        "SETPOINT_TEMP": 240,
        "DEVICE_UPTIME": "657827",
        "HEATING_UPTIME": "104954",
        "ERRORS": "0",
        "STATUS_FLAGS": [{"WINDOW_OPEN_DETECTED": 0, "HEATING_ON": 0}],
    }
    setup_mock_response(mock_session, mock_data)
    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=mock_session
    )

    status = await client.get_statuses()

    assert status.hw_version == 257
    assert status.fw_version == 265
    assert status.device_uptime == 657827
    assert status.heating_uptime == 104954
    assert status.errors == 0


@pytest.mark.asyncio
async def test_session_creation_and_closing() -> None:
    """Test automatic session creation and cleanup."""
    client = AirobotClient("192.168.1.100", "test_user", "test_pass")
    assert client._session is None

    session = await client._get_session()
    assert session is not None
    assert client._session is session
    assert client._close_session is True

    session2 = await client._get_session()
    assert session2 is session

    await client.close()
    assert client._session is None


@pytest.mark.asyncio
async def test_session_provided_externally() -> None:
    """Test behavior when session is provided externally."""
    external_session = MagicMock(spec=aiohttp.ClientSession)
    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=external_session
    )

    session = await client._get_session()
    assert session is external_session
    assert client._close_session is False

    await client.close()
    assert client._session is external_session


@pytest.mark.asyncio
async def test_validation_warnings(
    client: AirobotClient, caplog: pytest.LogCaptureFixture
) -> None:
    """Test validation warnings for out-of-range values."""
    invalid_data = {
        "DEVICE_ID": "T01TEST123",
        "HW_VERSION": 100,
        "FW_VERSION": 1000,
        "TEMP_AIR": -10000,
        "HUM_AIR": 70000,
        "TEMP_FLOOR": 300,
        "CO2": 800,
        "AQI": 10,
        "DEVICE_UPTIME": 124,
        "HEATING_UPTIME": 117,
        "ERRORS": 0,
        "SETPOINT_TEMP": 10,
        "STATUS_FLAGS": [{"WINDOW_OPEN_DETECTED": 0, "HEATING_ON": 1}],
    }
    setup_mock_response(client._session, invalid_data)

    with caplog.at_level("WARNING"):
        status = await client.get_statuses()

    assert isinstance(status, ThermostatStatus)
    assert status.device_id == "T01TEST123"

    warning_messages = [r.message for r in caplog.records if r.levelname == "WARNING"]
    assert any("HW_VERSION" in msg and "100" in msg for msg in warning_messages)
    assert any("FW_VERSION" in msg and "1000" in msg for msg in warning_messages)
    assert any("AQI" in msg and "10" in msg for msg in warning_messages)
