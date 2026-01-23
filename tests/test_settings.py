"""Tests for pyairobotrest settings functionality."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from pyairobotrest.client import AirobotClient
from pyairobotrest.models import SettingFlags, ThermostatSettings


@pytest.mark.asyncio
async def test_get_settings() -> None:
    """Test getting thermostat settings."""
    mock_session = MagicMock()
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "DEVICE_ID": "T01648142",
        "MODE": 1,
        "SETPOINT_TEMP": 220,
        "SETPOINT_TEMP_AWAY": 180,
        "HYSTERESIS_BAND": 1,
        "DEVICE_NAME": "Bedroom",
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
    mock_response.status = 200
    mock_session.request.return_value.__aenter__.return_value = mock_response

    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=mock_session
    )
    settings = await client.get_settings()

    assert isinstance(settings, ThermostatSettings)
    assert settings.device_id == "T01648142"
    assert settings.mode == 1
    assert settings.setpoint_temp == 22.0
    assert settings.setpoint_temp_away == 18.0
    assert settings.hysteresis_band == 0.1
    assert settings.device_name == "Bedroom"
    assert not settings.setting_flags.reboot


@pytest.mark.asyncio
async def test_setting_flags_from_dict() -> None:
    """Test SettingFlags creation from dictionary."""
    data = {
        "REBOOT": 1,
        "ACTUATOR_EXERCISE_DISABLED": 0,
        "RECALIBRATE_CO2": 1,
        "CHILDLOCK_ENABLED": 0,
        "BOOST_ENABLED": 1,
    }

    flags = SettingFlags.from_dict(data)
    assert flags.reboot is True
    assert flags.actuator_exercise_disabled is False
    assert flags.recalibrate_co2 is True
    assert flags.childlock_enabled is False
    assert flags.boost_enabled is True


@pytest.mark.asyncio
async def test_setting_flags_to_dict() -> None:
    """Test SettingFlags conversion to dictionary."""
    flags = SettingFlags(
        reboot=True,
        actuator_exercise_disabled=False,
        recalibrate_co2=True,
        childlock_enabled=False,
        boost_enabled=True,
    )

    assert flags.to_dict() == {
        "REBOOT": 1,
        "ACTUATOR_EXERCISE_DISABLED": 0,
        "RECALIBRATE_CO2": 1,
        "CHILDLOCK_ENABLED": 0,
        "BOOST_ENABLED": 1,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mode,expected_home,expected_away",
    [
        (1, True, False),
        (2, False, True),
    ],
)
async def test_settings_mode_properties(
    mode: int, expected_home: bool, expected_away: bool
) -> None:
    """Test ThermostatSettings mode helper properties."""
    flags = SettingFlags(
        reboot=False,
        actuator_exercise_disabled=False,
        recalibrate_co2=False,
        childlock_enabled=False,
        boost_enabled=False,
    )

    settings = ThermostatSettings(
        device_id="T01648142",
        mode=mode,
        setpoint_temp=22.0,
        setpoint_temp_away=18.0,
        hysteresis_band=0.1,
        device_name="Test",
        setting_flags=flags,
    )
    assert settings.is_home_mode is expected_home
    assert settings.is_away_mode is expected_away


@pytest.mark.asyncio
async def test_settings_string_conversion() -> None:
    """Test ThermostatSettings handles string values from real API."""
    mock_session = MagicMock()
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "DEVICE_ID": "T01648142",
        "MODE": "1",
        "SETPOINT_TEMP": "220",
        "SETPOINT_TEMP_AWAY": "180",
        "HYSTERESIS_BAND": "1",
        "DEVICE_NAME": "Bedroom",
        "SETTING_FLAGS": [
            {
                "REBOOT": "0",
                "ACTUATOR_EXERCISE_DISABLED": "0",
                "RECALIBRATE_CO2": "0",
                "CHILDLOCK_ENABLED": "1",
                "BOOST_ENABLED": "0",
            }
        ],
    }
    mock_response.status = 200
    mock_session.request.return_value.__aenter__.return_value = mock_response

    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=mock_session
    )
    settings = await client.get_settings()

    assert settings.mode == 1
    assert settings.setpoint_temp == 22.0
    assert settings.setting_flags.childlock_enabled is True


@pytest.mark.asyncio
async def test_settings_validation_warnings(caplog: pytest.LogCaptureFixture) -> None:
    """Test that out-of-range settings values generate warnings."""
    data = {
        "DEVICE_ID": "T01648142",
        "MODE": 9999,
        "SETPOINT_TEMP": 40,
        "SETPOINT_TEMP_AWAY": 400,
        "HYSTERESIS_BAND": 600,
        "DEVICE_NAME": "ThisNameIsWayTooLongForDevice",
        "SETTING_FLAGS": [{}],
    }

    ThermostatSettings.from_dict(data)

    assert "MODE" in caplog.text
    assert "SETPOINT_TEMP" in caplog.text
    assert "DEVICE_NAME" in caplog.text


@pytest.mark.asyncio
async def test_settings_to_dict() -> None:
    """Test ThermostatSettings to_dict conversion."""
    flags = SettingFlags(
        reboot=False,
        actuator_exercise_disabled=True,
        recalibrate_co2=False,
        childlock_enabled=True,
        boost_enabled=False,
    )

    settings = ThermostatSettings(
        device_id="T01648142",
        mode=2,
        setpoint_temp=23.5,
        setpoint_temp_away=16.5,
        hysteresis_band=0.3,
        device_name="Kitchen",
        setting_flags=flags,
    )

    result = settings.to_dict()
    assert result == {
        "MODE": 2,
        "SETPOINT_TEMP": 235,
        "SETPOINT_TEMP_AWAY": 165,
        "HYSTERESIS_BAND": 3,
        "DEVICE_NAME": "Kitchen",
        "SETTING_FLAGS": [
            {
                "REBOOT": 0,
                "ACTUATOR_EXERCISE_DISABLED": 1,
                "RECALIBRATE_CO2": 0,
                "CHILDLOCK_ENABLED": 1,
                "BOOST_ENABLED": 0,
            }
        ],
    }
    assert "DEVICE_ID" not in result
