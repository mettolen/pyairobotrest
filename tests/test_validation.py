"""Tests for validation methods in the Airobot client."""
# pylint: disable=redefined-outer-name

import pytest

from pyairobotrest import AirobotClient
from pyairobotrest.exceptions import AirobotError


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_name,args,expected_error",
    [
        # Mode validation
        ("set_mode", (0,), "Mode must be between 1 and 2"),
        ("set_mode", (3,), "Mode must be between 1 and 2"),
        # Home temperature validation
        (
            "set_home_temperature",
            (4.9,),
            "HOME temperature must be between 5.0°C and 35.0°C",
        ),
        (
            "set_home_temperature",
            (35.1,),
            "HOME temperature must be between 5.0°C and 35.0°C",
        ),
        # Away temperature validation
        (
            "set_away_temperature",
            (4.9,),
            "AWAY temperature must be between 5.0°C and 35.0°C",
        ),
        (
            "set_away_temperature",
            (35.1,),
            "AWAY temperature must be between 5.0°C and 35.0°C",
        ),
        # Hysteresis validation
        (
            "set_hysteresis_band",
            (-0.1,),
            "Hysteresis band must be between 0.0°C and 0.5°C",
        ),
        (
            "set_hysteresis_band",
            (0.6,),
            "Hysteresis band must be between 0.0°C and 0.5°C",
        ),
        # Device name validation
        ("set_device_name", (12345,), "Device name must be a string"),
        (
            "set_device_name",
            ("",),
            "Device name length must be between 1 and 20 characters",
        ),
        (
            "set_device_name",
            ("A" * 21,),
            "Device name length must be between 1 and 20 characters",
        ),
        # Boolean flag validation
        ("set_child_lock", ("true",), "Child lock must be a boolean"),
        ("set_boost_mode", (1,), "Boost mode must be a boolean"),
        (
            "toggle_actuator_exercise",
            ("false",),
            "Actuator exercise disabled must be a boolean",
        ),
    ],
)
async def test_validation_errors(
    validation_client: AirobotClient,
    method_name: str,
    args: tuple[str, ...],
    expected_error: str,
) -> None:
    """Test validation methods that raise errors for invalid inputs."""
    method = getattr(validation_client, method_name)
    with pytest.raises(AirobotError, match=expected_error):
        await method(*args)
