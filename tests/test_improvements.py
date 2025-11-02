"""Tests for new specific code improvements."""

import logging
from unittest.mock import MagicMock, Mock

import aiohttp
import pytest
from pyairobotrest import AirobotClient
from pyairobotrest.models import ThermostatSettings, ThermostatStatus


class TestFactoryMethod:
    """Tests for AirobotClient.create() factory method."""

    @pytest.mark.asyncio
    async def test_create_factory_method(self):
        """Test that factory method creates a client with initialized session."""
        client = await AirobotClient.create(
            host="192.168.1.100",
            username="T01TEST",
            password="test_pass",
        )

        # Verify client was created
        assert client.host == "192.168.1.100"
        assert client.username == "T01TEST"
        assert client.password == "test_pass"

        # Verify session was initialized
        assert client._session is not None  # pylint: disable=protected-access

        await client.close()

    @pytest.mark.asyncio
    async def test_create_with_provided_session(self):
        """Test that factory method can accept a provided session."""
        provided_session = Mock()
        client = await AirobotClient.create(
            host="192.168.1.100",
            username="T01TEST",
            password="test_pass",
            session=provided_session,
        )

        # Verify the provided session is used
        assert client._session is provided_session  # pylint: disable=protected-access

        # Don't close since we didn't create the session


class TestStrictValidation:
    """Tests for strict validation mode in models."""

    def test_status_strict_validation_in_range(self):
        """Test that valid data passes strict validation."""
        data = {
            "DEVICE_ID": "T01TEST",
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

        # Should not raise with strict=True when data is valid
        status = ThermostatStatus.from_dict(data, strict=True)
        assert status.temp_air == 22.0
        assert status.hw_version == 256

    def test_status_strict_validation_out_of_range(self):
        """Test that strict validation raises for out-of-range values."""
        data = {
            "DEVICE_ID": "T01TEST",
            "HW_VERSION": 9999,  # Outside range
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

        # Should raise ValueError with strict=True
        with pytest.raises(ValueError, match="HW_VERSION"):
            ThermostatStatus.from_dict(data, strict=True)

    def test_status_non_strict_validation_logs_warning(self, caplog):
        """Test that non-strict validation logs warning but doesn't raise."""

        caplog.set_level(logging.WARNING)

        data = {
            "DEVICE_ID": "T01TEST",
            "HW_VERSION": 9999,  # Outside range
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

        # Should not raise with strict=False (default)
        status = ThermostatStatus.from_dict(data, strict=False)
        assert status.hw_version == 9999

        # But should log warning
        assert "HW_VERSION" in caplog.text
        assert "outside expected range" in caplog.text

    def test_settings_strict_validation_in_range(self):
        """Test that valid settings pass strict validation."""
        data = {
            "DEVICE_ID": "T01TEST",
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

        # Should not raise with strict=True when data is valid
        settings = ThermostatSettings.from_dict(data, strict=True)
        assert settings.setpoint_temp == 22.0
        assert settings.mode == 1

    def test_settings_strict_validation_invalid_mode(self):
        """Test that strict validation raises for invalid mode."""
        data = {
            "DEVICE_ID": "T01TEST",
            "MODE": 5,  # Invalid: must be 1 or 2
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

        # Should raise ValueError with strict=True
        with pytest.raises(ValueError, match="MODE"):
            ThermostatSettings.from_dict(data, strict=True)

    def test_settings_strict_validation_invalid_device_name(self):
        """Test that strict validation raises for invalid device name length."""
        data = {
            "DEVICE_ID": "T01TEST",
            "MODE": 1,
            "SETPOINT_TEMP": 220,
            "SETPOINT_TEMP_AWAY": 180,
            "HYSTERESIS_BAND": 1,
            "DEVICE_NAME": "x" * 25,  # Too long (max 20)
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

        # Should raise ValueError with strict=True
        with pytest.raises(ValueError, match="DEVICE_NAME"):
            ThermostatSettings.from_dict(data, strict=True)


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session for testing."""

    return MagicMock(spec=aiohttp.ClientSession)
