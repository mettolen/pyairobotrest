"""Simple integration tests for individual setting methods."""
# pylint: disable=redefined-outer-name,protected-access

from unittest.mock import MagicMock, patch

import aiohttp
import pytest
from pyairobotrest import AirobotClient


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = MagicMock(spec=aiohttp.ClientSession)
    return session


@pytest.fixture
def client(mock_session):
    """Create test client."""
    return AirobotClient(
        host="192.168.1.100",
        username="T01TEST123",
        password="test_password",
        session=mock_session,
    )


@pytest.fixture
def mock_settings_data():
    """Mock settings data."""
    return {
        "MODE": 1,
        "SETPOINT_TEMP": 220,
        "SETPOINT_TEMP_AWAY": 180,
        "HYSTERESIS_BAND": 20,
        "DEVICE_NAME": "Test",
        "SETTING_FLAGS": 0,
    }


class TestIndividualMethodsIntegration:
    """Integration tests for individual setting methods."""

    @pytest.mark.asyncio
    async def test_set_mode_integration(self, client):
        """Test set_mode method calls _set_partial_settings."""
        with patch.object(client, "_set_partial_settings") as mock_set:
            await client.set_mode(2)

            mock_set.assert_called_once_with(MODE=2)
            # Verify validation passed (mode 2 is valid AWAY mode)

    @pytest.mark.asyncio
    async def test_set_home_temperature_integration(self, client):
        """Test set_home_temperature method."""
        with patch.object(client, "_set_partial_settings") as mock_set:
            await client.set_home_temperature(23.5)

            mock_set.assert_called_once_with(SETPOINT_TEMP=235)
            # Verify conversion: 23.5°C * 10 = 235

    @pytest.mark.asyncio
    async def test_set_child_lock_integration(self, client):
        """Test set_child_lock method."""
        with patch.object(client, "_set_partial_settings") as mock_set:
            await client.set_child_lock(True)

            mock_set.assert_called_once_with(CHILDLOCK_ENABLED=1)
            # Verify flag conversion: True -> 1

    @pytest.mark.asyncio
    async def test_all_individual_methods_exist(self, client):
        """Test all individual methods exist and are callable."""
        methods = [
            "set_mode",
            "set_home_temperature",
            "set_away_temperature",
            "set_hysteresis_band",
            "set_device_name",
            "set_child_lock",
            "set_boost_mode",
            "reboot_thermostat",
            "recalibrate_co2_sensor",
            "toggle_actuator_exercise",
        ]

        for method_name in methods:
            assert hasattr(client, method_name)
            method = getattr(client, method_name)
            assert callable(method)
