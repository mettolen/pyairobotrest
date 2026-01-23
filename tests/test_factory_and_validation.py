"""Tests for factory method and strict validation features."""
# pylint: disable=protected-access

import logging
from unittest.mock import Mock

import pytest

from pyairobotrest import AirobotClient
from pyairobotrest.models import ThermostatSettings, ThermostatStatus


@pytest.mark.asyncio
async def test_create_factory_method() -> None:
    """Test that factory method creates a client with initialized session."""
    client = await AirobotClient.create(
        host="192.168.1.100",
        username="T01TEST",
        password="test_pass",
    )

    assert client.host == "192.168.1.100"
    assert client.username == "T01TEST"
    assert client.password == "test_pass"
    assert client._session is not None

    await client.close()


@pytest.mark.asyncio
async def test_create_with_provided_session() -> None:
    """Test that factory method can accept a provided session."""
    provided_session = Mock()
    client = await AirobotClient.create(
        host="192.168.1.100",
        username="T01TEST",
        password="test_pass",
        session=provided_session,
    )

    assert client._session is provided_session


@pytest.mark.parametrize(
    "hw_version,strict,should_raise",
    [
        (256, True, False),
        (9999, True, True),
        (9999, False, False),
    ],
)
def test_status_strict_validation(
    hw_version: int, strict: bool, should_raise: bool
) -> None:
    """Test strict validation for status data."""
    data = {
        "DEVICE_ID": "T01TEST",
        "HW_VERSION": hw_version,
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

    if should_raise:
        with pytest.raises(ValueError, match="HW_VERSION"):
            ThermostatStatus.from_dict(data, strict=strict)
    else:
        status = ThermostatStatus.from_dict(data, strict=strict)
        assert status.hw_version == hw_version


def test_status_non_strict_validation_logs_warning(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test that non-strict validation logs warning but doesn't raise."""
    caplog.set_level(logging.WARNING)

    data = {
        "DEVICE_ID": "T01TEST",
        "HW_VERSION": 9999,
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

    status = ThermostatStatus.from_dict(data, strict=False)
    assert status.hw_version == 9999
    assert "HW_VERSION" in caplog.text
    assert "outside expected range" in caplog.text


@pytest.mark.parametrize(
    "field,value,should_raise",
    [
        ("MODE", 1, False),
        ("MODE", 5, True),
        ("DEVICE_NAME", "Test", False),
        ("DEVICE_NAME", "x" * 25, True),
    ],
)
def test_settings_strict_validation(
    field: str, value: int | str, should_raise: bool
) -> None:
    """Test strict validation for settings data."""
    data = {
        "DEVICE_ID": "T01TEST",
        "MODE": 1,
        "SETPOINT_TEMP": 220,
        "SETPOINT_TEMP_AWAY": 180,
        "HYSTERESIS_BAND": 1,
        "DEVICE_NAME": "Test",
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
    data[field] = value

    if should_raise:
        with pytest.raises(ValueError, match=field):
            ThermostatSettings.from_dict(data, strict=True)
    else:
        settings = ThermostatSettings.from_dict(data, strict=True)
        assert settings.mode in (1, 2)
