"""Tests for pyairobotrest settings functionality."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from pyairobotrest.client import AirobotClient
from pyairobotrest.models import SettingFlags, ThermostatSettings


@pytest.mark.asyncio
async def test_get_settings():
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

    # Mock successful response
    mock_session.request.return_value.__aenter__.return_value = mock_response
    mock_response.status = 200

    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=mock_session
    )
    settings = await client.get_settings()

    assert isinstance(settings, ThermostatSettings)
    assert settings.device_id == "T01648142"
    assert settings.mode == 1
    assert settings.setpoint_temp == 22.0  # Converted from 220 (0.1°C units)
    assert settings.setpoint_temp_away == 18.0  # Converted from 180
    assert settings.hysteresis_band == 0.1  # Converted from 1
    assert settings.device_name == "Bedroom"
    assert not settings.setting_flags.reboot
    assert not settings.setting_flags.actuator_exercise_disabled
    assert not settings.setting_flags.recalibrate_co2
    assert not settings.setting_flags.childlock_enabled
    assert not settings.setting_flags.boost_enabled


# test_set_settings removed - set_settings() method no longer exists
# Use individual setter methods instead (set_mode, set_home_temperature, etc.)


@pytest.mark.asyncio
async def test_setting_flags_from_dict():
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
async def test_setting_flags_to_dict():
    """Test SettingFlags conversion to dictionary."""
    flags = SettingFlags(
        reboot=True,
        actuator_exercise_disabled=False,
        recalibrate_co2=True,
        childlock_enabled=False,
        boost_enabled=True,
    )

    result = flags.to_dict()
    expected = {
        "REBOOT": 1,
        "ACTUATOR_EXERCISE_DISABLED": 0,
        "RECALIBRATE_CO2": 1,
        "CHILDLOCK_ENABLED": 0,
        "BOOST_ENABLED": 1,
    }
    assert result == expected


@pytest.mark.asyncio
async def test_thermostat_settings_properties():
    """Test ThermostatSettings helper properties."""
    setting_flags = SettingFlags(
        reboot=False,
        actuator_exercise_disabled=False,
        recalibrate_co2=False,
        childlock_enabled=False,
        boost_enabled=False,
    )

    # Test HOME mode
    settings_home = ThermostatSettings(
        device_id="T01648142",
        mode=1,
        setpoint_temp=22.0,
        setpoint_temp_away=18.0,
        hysteresis_band=0.1,
        device_name="Test",
        setting_flags=setting_flags,
    )
    assert settings_home.is_home_mode is True
    assert settings_home.is_away_mode is False

    # Test AWAY mode
    settings_away = ThermostatSettings(
        device_id="T01648142",
        mode=2,
        setpoint_temp=22.0,
        setpoint_temp_away=18.0,
        hysteresis_band=0.1,
        device_name="Test",
        setting_flags=setting_flags,
    )
    assert settings_away.is_home_mode is False
    assert settings_away.is_away_mode is True


@pytest.mark.asyncio
async def test_thermostat_settings_string_conversion():
    """Test ThermostatSettings handles string values from real API."""
    mock_session = MagicMock()
    mock_response = AsyncMock()
    mock_response.json.return_value = {
        "DEVICE_ID": "T01648142",
        "MODE": "1",  # String value as from real API
        "SETPOINT_TEMP": "220",  # String value
        "SETPOINT_TEMP_AWAY": "180",
        "HYSTERESIS_BAND": "1",
        "DEVICE_NAME": "Bedroom",
        "SETTING_FLAGS": [
            {
                "REBOOT": "0",  # String values
                "ACTUATOR_EXERCISE_DISABLED": "0",
                "RECALIBRATE_CO2": "0",
                "CHILDLOCK_ENABLED": "1",
                "BOOST_ENABLED": "0",
            }
        ],
    }

    # Mock successful response
    mock_session.request.return_value.__aenter__.return_value = mock_response
    mock_response.status = 200

    client = AirobotClient(
        "192.168.1.100", "test_user", "test_pass", session=mock_session
    )
    settings = await client.get_settings()

    assert settings.mode == 1
    assert settings.setpoint_temp == 22.0
    assert settings.setpoint_temp_away == 18.0
    assert settings.hysteresis_band == 0.1
    assert settings.setting_flags.childlock_enabled is True


@pytest.mark.asyncio
async def test_settings_validation_warnings(caplog):
    """Test that out-of-range settings values generate warnings."""
    data = {
        "DEVICE_ID": "T01648142",
        "MODE": 9999,  # Out of range (max is 2)
        "SETPOINT_TEMP": 40,  # Out of range (4.0°C, below minimum 5.0°C)
        "SETPOINT_TEMP_AWAY": 400,  # Out of range (40.0°C, above maximum 35.0°C)
        "HYSTERESIS_BAND": 600,  # Out of range (60.0°C, above maximum 5.0°C)
        "DEVICE_NAME": "ThisNameIsWayTooLongForDevice",  # Too long (> 20 chars)
        "SETTING_FLAGS": [{}],
    }

    ThermostatSettings.from_dict(data)

    # Check that warnings were logged
    assert "MODE" in caplog.text
    assert "SETPOINT_TEMP" in caplog.text
    assert "SETPOINT_TEMP_AWAY" in caplog.text
    assert "HYSTERESIS_BAND" in caplog.text
    assert "DEVICE_NAME" in caplog.text


@pytest.mark.asyncio
async def test_settings_to_dict():
    """Test ThermostatSettings to_dict conversion."""
    setting_flags = SettingFlags(
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
        setting_flags=setting_flags,
    )

    result = settings.to_dict()
    expected = {
        "MODE": 2,
        "SETPOINT_TEMP": 235,  # 23.5 * 10
        "SETPOINT_TEMP_AWAY": 165,  # 16.5 * 10
        "HYSTERESIS_BAND": 3,  # 0.3 * 10
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
    assert result == expected
    # Verify DEVICE_ID is not included (read-only)
    assert "DEVICE_ID" not in result
