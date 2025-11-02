"""Tests for validation methods in the Airobot client."""

# pylint: disable=redefined-outer-name
# Fixtures are intentionally passed as arguments to test functions

import pytest
from pyairobotrest import AirobotClient
from pyairobotrest.exceptions import AirobotError


@pytest.fixture
def validation_client():
    """Create test client for validation tests."""
    return AirobotClient("192.168.1.100", "T01234567", "password123")


class TestValidationMethods:
    """Test validation methods that raise errors for invalid inputs."""

    @pytest.mark.asyncio
    async def test_validate_mode_below_min(self, validation_client):
        """Test mode validation with value below minimum."""
        with pytest.raises(AirobotError, match="Mode must be between 1 and 2"):
            await validation_client.set_mode(0)

    @pytest.mark.asyncio
    async def test_validate_mode_above_max(self, validation_client):
        """Test mode validation with value above maximum."""
        with pytest.raises(AirobotError, match="Mode must be between 1 and 2"):
            await validation_client.set_mode(3)

    @pytest.mark.asyncio
    async def test_validate_home_temperature_below_min(self, validation_client):
        """Test home temperature validation with value below minimum."""
        with pytest.raises(
            AirobotError, match="HOME temperature must be between 5.0°C and 35.0°C"
        ):
            await validation_client.set_home_temperature(4.9)

    @pytest.mark.asyncio
    async def test_validate_home_temperature_above_max(self, validation_client):
        """Test home temperature validation with value above maximum."""
        with pytest.raises(
            AirobotError, match="HOME temperature must be between 5.0°C and 35.0°C"
        ):
            await validation_client.set_home_temperature(35.1)

    @pytest.mark.asyncio
    async def test_validate_away_temperature_below_min(self, validation_client):
        """Test away temperature validation with value below minimum."""
        with pytest.raises(
            AirobotError, match="AWAY temperature must be between 5.0°C and 35.0°C"
        ):
            await validation_client.set_away_temperature(4.9)

    @pytest.mark.asyncio
    async def test_validate_away_temperature_above_max(self, validation_client):
        """Test away temperature validation with value above maximum."""
        with pytest.raises(
            AirobotError, match="AWAY temperature must be between 5.0°C and 35.0°C"
        ):
            await validation_client.set_away_temperature(35.1)

    @pytest.mark.asyncio
    async def test_validate_hysteresis_below_min(self, validation_client):
        """Test hysteresis validation with value below minimum."""
        with pytest.raises(
            AirobotError,
            match="Hysteresis band must be between 0.0°C and 0.5°C",
        ):
            await validation_client.set_hysteresis_band(-0.1)

    @pytest.mark.asyncio
    async def test_validate_hysteresis_above_max(self, validation_client):
        """Test hysteresis validation with value above maximum."""
        with pytest.raises(
            AirobotError,
            match="Hysteresis band must be between 0.0°C and 0.5°C",
        ):
            await validation_client.set_hysteresis_band(0.6)

    @pytest.mark.asyncio
    async def test_validate_device_name_not_string(self, validation_client):
        """Test device name validation with non-string value."""
        with pytest.raises(AirobotError, match="Device name must be a string"):
            await validation_client.set_device_name(12345)  # type: ignore

    @pytest.mark.asyncio
    async def test_validate_device_name_too_short(self, validation_client):
        """Test device name validation with name too short."""
        with pytest.raises(
            AirobotError,
            match="Device name length must be between 1 and 20 characters",
        ):
            await validation_client.set_device_name("")

    @pytest.mark.asyncio
    async def test_validate_device_name_too_long(self, validation_client):
        """Test device name validation with name too long."""
        with pytest.raises(
            AirobotError,
            match="Device name length must be between 1 and 20 characters",
        ):
            await validation_client.set_device_name("A" * 21)

    @pytest.mark.asyncio
    async def test_validate_child_lock_not_bool(self, validation_client):
        """Test child lock validation with non-boolean value."""
        with pytest.raises(AirobotError, match="Child lock must be a boolean"):
            await validation_client.set_child_lock("true")  # type: ignore

    @pytest.mark.asyncio
    async def test_validate_boost_mode_not_bool(self, validation_client):
        """Test boost mode validation with non-boolean value."""
        with pytest.raises(AirobotError, match="Boost mode must be a boolean"):
            await validation_client.set_boost_mode(1)  # type: ignore

    @pytest.mark.asyncio
    async def test_validate_actuator_exercise_not_bool(self, validation_client):
        """Test actuator exercise validation with non-boolean value."""
        with pytest.raises(
            AirobotError, match="Actuator exercise disabled must be a boolean"
        ):
            await validation_client.toggle_actuator_exercise("false")  # type: ignore
