"""Integration tests for all setter methods."""

# pylint: disable=redefined-outer-name
# Fixtures are intentionally passed as arguments to test functions

import logging
from unittest.mock import AsyncMock, MagicMock

import pytest
from pyairobotrest import AirobotClient


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = MagicMock()
    response = AsyncMock()
    response.status = 200
    response.json.return_value = {}
    response.headers = {"Content-Type": "application/json"}  # Proper dict for headers
    session.request.return_value.__aenter__.return_value = response
    return session


@pytest.fixture
def client(mock_session):
    """Create test client with mocked session."""
    return AirobotClient(
        "192.168.1.100", "T01234567", "password123", session=mock_session
    )


class TestSetterMethodsIntegration:
    """Test all setter methods with actual API calls (mocked)."""

    @pytest.mark.asyncio
    async def test_set_mode_success(self, client, mock_session):
        """Test successful mode setting."""
        await client.set_mode(1)

        # Verify request was made
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"MODE": 1}

    @pytest.mark.asyncio
    async def test_set_home_temperature_success(self, client, mock_session):
        """Test successful home temperature setting."""
        await client.set_home_temperature(22.5)

        # Verify request was made with converted value
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"SETPOINT_TEMP": 225}

    @pytest.mark.asyncio
    async def test_set_away_temperature_success(self, client, mock_session):
        """Test successful away temperature setting."""
        await client.set_away_temperature(18.0)

        # Verify request was made with converted value
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"SETPOINT_TEMP_AWAY": 180}

    @pytest.mark.asyncio
    async def test_set_hysteresis_band_success(self, client, mock_session):
        """Test successful hysteresis band setting."""
        await client.set_hysteresis_band(0.3)

        # Verify request was made with converted value
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"HYSTERESIS_BAND": 3}

    @pytest.mark.asyncio
    async def test_set_device_name_success(self, client, mock_session):
        """Test successful device name setting."""
        await client.set_device_name("Kitchen")

        # Verify request was made
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"DEVICE_NAME": "Kitchen"}

    @pytest.mark.asyncio
    async def test_set_child_lock_enabled(self, client, mock_session):
        """Test enabling child lock."""
        await client.set_child_lock(True)

        # Verify request was made with converted boolean
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"CHILDLOCK_ENABLED": 1}

    @pytest.mark.asyncio
    async def test_set_child_lock_disabled(self, client, mock_session):
        """Test disabling child lock."""
        await client.set_child_lock(False)

        # Verify request was made with converted boolean
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"CHILDLOCK_ENABLED": 0}

    @pytest.mark.asyncio
    async def test_set_boost_mode_enabled(self, client, mock_session):
        """Test enabling boost mode."""
        await client.set_boost_mode(True)

        # Verify request was made
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"BOOST_ENABLED": 1}

    @pytest.mark.asyncio
    async def test_set_boost_mode_disabled(self, client, mock_session):
        """Test disabling boost mode."""
        await client.set_boost_mode(False)

        # Verify request was made
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"BOOST_ENABLED": 0}

    @pytest.mark.asyncio
    async def test_reboot_thermostat(self, client, mock_session):
        """Test rebooting the thermostat."""
        await client.reboot_thermostat()

        # Verify request was made
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"REBOOT": 1}

    @pytest.mark.asyncio
    async def test_recalibrate_co2_sensor(self, client, mock_session):
        """Test recalibrating CO2 sensor."""
        await client.recalibrate_co2_sensor()

        # Verify request was made
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"RECALIBRATE_CO2": 1}

    @pytest.mark.asyncio
    async def test_toggle_actuator_exercise_disabled(self, client, mock_session):
        """Test disabling actuator exercise."""
        await client.toggle_actuator_exercise(True)

        # Verify request was made
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"ACTUATOR_EXERCISE_DISABLED": 1}

    @pytest.mark.asyncio
    async def test_toggle_actuator_exercise_enabled(self, client, mock_session):
        """Test enabling actuator exercise."""
        await client.toggle_actuator_exercise(False)

        # Verify request was made
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[1]["json"] == {"ACTUATOR_EXERCISE_DISABLED": 0}

    @pytest.mark.asyncio
    async def test_logging_on_post_request(self, client, caplog):
        """Test that POST requests log request and response details."""

        caplog.set_level(logging.DEBUG)

        await client.set_mode(2)

        # Check that logging occurred
        assert "POST" in caplog.text
        assert "setSettings" in caplog.text
