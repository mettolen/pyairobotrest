"""Tests for all setter methods in Airobot client."""
# pylint: disable=redefined-outer-name,protected-access

import logging
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import aiohttp
import pytest

from pyairobotrest import AirobotClient
from pyairobotrest.exceptions import AirobotAuthError, AirobotError
from pyairobotrest.models import SettingFlags, ThermostatMode, ThermostatSettings

from .conftest import setup_mock_response

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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "side_effect",
    [
        pytest.param(aiohttp.ClientError("Connection reset"), id="connection_error"),
        pytest.param(TimeoutError("Request timeout"), id="timeout_error"),
    ],
)
async def test_reboot_suppresses_expected_connection_errors(
    client: AirobotClient, side_effect: Exception
) -> None:
    """Test reboot suppresses connection/timeout errors from the dropped socket."""
    client._session.request = MagicMock(  # type: ignore[union-attr, method-assign]
        side_effect=side_effect
    )

    await client.reboot_thermostat()


@pytest.mark.asyncio
async def test_reboot_propagates_auth_error(client: AirobotClient) -> None:
    """Test reboot still raises when authentication fails."""
    setup_mock_response(client._session, {}, status=401)

    with pytest.raises(AirobotAuthError):
        await client.reboot_thermostat()


@pytest.mark.asyncio
async def test_set_mode_accepts_enum(
    client_with_response: AirobotClient, mock_session_with_response: Any
) -> None:
    """Test set_mode accepts a ThermostatMode member."""
    await client_with_response.set_mode(ThermostatMode.AWAY)

    payload = mock_session_with_response.request.call_args[1]["json"]
    assert payload == {"MODE": 2}


def _make_settings(
    *, device_name: str = "Kitchen", reboot: bool = False, recalibrate: bool = False
) -> ThermostatSettings:
    """Build a ThermostatSettings instance for set_settings tests."""
    return ThermostatSettings(
        device_id="T01TEST123",
        mode=ThermostatMode.AWAY,
        setpoint_temp=21.0,
        setpoint_temp_away=17.0,
        hysteresis_band=0.2,
        device_name=device_name,
        setting_flags=SettingFlags(
            reboot=reboot,
            actuator_exercise_disabled=True,
            recalibrate_co2=recalibrate,
            childlock_enabled=True,
            boost_enabled=False,
        ),
    )


@pytest.mark.asyncio
async def test_set_settings_sends_full_payload_and_guards_flags(
    client_with_response: AirobotClient, mock_session_with_response: Any
) -> None:
    """Test set_settings writes all fields and forces transient flags off."""
    await client_with_response.set_settings(
        _make_settings(reboot=True, recalibrate=True)
    )

    payload = mock_session_with_response.request.call_args[1]["json"]
    assert payload["MODE"] == 2
    assert payload["SETPOINT_TEMP"] == 210
    assert payload["SETPOINT_TEMP_AWAY"] == 170
    assert payload["HYSTERESIS_BAND"] == 2
    assert payload["DEVICE_NAME"] == "Kitchen"
    flags = payload["SETTING_FLAGS"][0]
    assert flags["REBOOT"] == 0
    assert flags["RECALIBRATE_CO2"] == 0
    assert flags["ACTUATOR_EXERCISE_DISABLED"] == 1
    assert flags["CHILDLOCK_ENABLED"] == 1


@pytest.mark.asyncio
async def test_set_settings_omits_empty_device_name(
    client_with_response: AirobotClient, mock_session_with_response: Any
) -> None:
    """Test set_settings omits an empty device name from the payload."""
    await client_with_response.set_settings(_make_settings(device_name=""))

    payload = mock_session_with_response.request.call_args[1]["json"]
    assert "DEVICE_NAME" not in payload


@pytest.mark.asyncio
async def test_set_settings_validates_before_sending(
    client_with_response: AirobotClient, mock_session_with_response: Any
) -> None:
    """Test set_settings validates values and does not send on failure."""
    settings = _make_settings()
    settings.mode = 5

    with pytest.raises(AirobotError):
        await client_with_response.set_settings(settings)

    mock_session_with_response.request.assert_not_called()
