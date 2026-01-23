"""Tests for all setter methods in Airobot client."""
# pylint: disable=redefined-outer-name,protected-access

import logging
from typing import TYPE_CHECKING, Any

import pytest

from pyairobotrest import AirobotClient

if TYPE_CHECKING:
    pass


@pytest.fixture
def client_with_response(mock_session_with_response: Any) -> AirobotClient:
    """Create test client with mocked session that returns successful response."""
    return AirobotClient(
        "192.168.1.100",
        "T01TEST123",
        "password123",
        session=mock_session_with_response,
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method_name,args,expected_json",
    [
        ("set_mode", (1,), {"MODE": 1}),
        ("set_mode", (2,), {"MODE": 2}),
        ("set_home_temperature", (22.5,), {"SETPOINT_TEMP": 225}),
        ("set_away_temperature", (18.0,), {"SETPOINT_TEMP_AWAY": 180}),
        ("set_hysteresis_band", (0.3,), {"HYSTERESIS_BAND": 3}),
        ("set_device_name", ("Kitchen",), {"DEVICE_NAME": "Kitchen"}),
        ("set_child_lock", (True,), {"CHILDLOCK_ENABLED": 1}),
        ("set_child_lock", (False,), {"CHILDLOCK_ENABLED": 0}),
        ("set_boost_mode", (True,), {"BOOST_ENABLED": 1}),
        ("set_boost_mode", (False,), {"BOOST_ENABLED": 0}),
        ("reboot_thermostat", (), {"REBOOT": 1}),
        ("recalibrate_co2_sensor", (), {"RECALIBRATE_CO2": 1}),
        ("toggle_actuator_exercise", (True,), {"ACTUATOR_EXERCISE_DISABLED": 1}),
        ("toggle_actuator_exercise", (False,), {"ACTUATOR_EXERCISE_DISABLED": 0}),
    ],
)
async def test_setter_methods(
    client_with_response: AirobotClient,
    mock_session_with_response: Any,
    method_name: str,
    args: tuple[Any, ...],
    expected_json: dict[str, Any],
) -> None:
    """Test all setter methods with various inputs."""
    method = getattr(client_with_response, method_name)
    await method(*args)

    mock_session_with_response.request.assert_called_once()
    call_args = mock_session_with_response.request.call_args
    assert call_args[1]["json"] == expected_json


@pytest.mark.asyncio
async def test_logging_on_post_request(
    client_with_response: AirobotClient, caplog: pytest.LogCaptureFixture
) -> None:
    """Test that POST requests log details at debug level."""
    caplog.set_level(logging.DEBUG)
    await client_with_response.set_mode(2)

    assert "POST" in caplog.text
    assert "setSettings" in caplog.text
