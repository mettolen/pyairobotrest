"""Airobot thermostat REST API client."""

__all__ = ["AirobotClient"]

import base64
import logging
from typing import Any

import aiohttp

from .const import (
    API_BASE_PATH,
    API_ENDPOINT_GET_SETTINGS,
    API_ENDPOINT_GET_STATUSES,
    API_ENDPOINT_SET_SETTINGS,
    DEFAULT_PORT,
    DEFAULT_TIMEOUT,
    DEVICE_NAME_MAX_LENGTH,
    DEVICE_NAME_MIN_LENGTH,
    HYSTERESIS_BAND_MAX,
    HYSTERESIS_BAND_MIN,
    METHOD_GET,
    METHOD_POST,
    MODE_MAX,
    MODE_MIN,
    SETPOINT_TEMP_RAW_MAX,
    SETPOINT_TEMP_RAW_MIN,
)
from .exceptions import (
    AirobotAuthError,
    AirobotConnectionError,
    AirobotError,
    AirobotTimeoutError,
)
from .models import ThermostatMode, ThermostatSettings, ThermostatStatus

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())


class AirobotClient:
    """Client for Airobot thermostat REST API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        port: int = DEFAULT_PORT,
        session: aiohttp.ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the Airobot client.

        Args:
            host: The hostname (like "airobot-thermostat-t01xxxxxx.local") or IP
                address of the Airobot thermostat.
            username: The thermostat device ID (e.g., "T01XXXXXX").
            password: The thermostat password.
                Password can be found in the thermostat menu under the
                "Mobile app" screen.
            port: The port number (default: 80).
            session: Optional aiohttp ClientSession to use.
            timeout: Request timeout in seconds (default: 10).
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self._session = session
        self._timeout = timeout
        self._close_session = False
        self._auth_header = self._create_auth_header()
        _LOGGER.debug(
            "Initialized AirobotClient "
            "(host=%s, port=%d, timeout=%ds, external_session=%s)",
            self.host,
            self.port,
            self._timeout,
            session is not None,
        )

    @classmethod
    async def create(
        cls,
        host: str,
        username: str,
        password: str,
        port: int = DEFAULT_PORT,
        session: aiohttp.ClientSession | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> "AirobotClient":
        """Create and initialize an Airobot client (factory method).

        This factory method ensures the session is ready for use, making it ideal
        for Home Assistant integrations and other async contexts where session
        initialization should be explicit.

        Args:
            host: The hostname or IP address of the Airobot thermostat.
            username: The thermostat device ID (e.g., "T01XXXXXX").
            password: The thermostat password.
            port: The port number (default: 80).
            session: Optional aiohttp ClientSession to use.
            timeout: Request timeout in seconds (default: 10).

        Returns:
            Initialized AirobotClient instance.

        Example:
            >>> client = await AirobotClient.create(
            ...     "192.168.1.100", "T01XXXXXX", "password"
            ... )
        """
        instance = cls(host, username, password, port, session, timeout)
        # Eagerly bind the session while inside a running event loop. When no
        # external session is supplied this creates the client-owned session up
        # front (and only then), so the connection pool is tied to this loop
        # rather than being lazily created on the first request.
        await instance._get_session()
        return instance

    def _create_auth_header(self) -> str:
        """Create Basic Auth header."""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self._session is None:
            _LOGGER.debug("Creating new aiohttp ClientSession")
            self._session = aiohttp.ClientSession()
            self._close_session = True
        return self._session

    async def close(self) -> None:
        """Close the client session."""
        if self._close_session and self._session:
            _LOGGER.debug("Closing aiohttp ClientSession")
            await self._session.close()
            self._session = None

    async def __aenter__(self) -> "AirobotClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        await self.close()

    def _build_url(self, endpoint: str) -> str:
        """Build the full URL for an API endpoint."""
        return f"http://{self.host}:{self.port}{API_BASE_PATH}{endpoint}"

    async def _request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the Airobot API.

        Args:
            method: HTTP method (GET, POST, etc.).
            endpoint: API endpoint path.
            json_data: Optional JSON data to send.

        Returns:
            Response data as dictionary.

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotTimeoutError: If request times out.
            AirobotAuthError: If authentication fails.
            AirobotError: For other API errors.
        """
        session = await self._get_session()
        url = self._build_url(endpoint)
        headers = {"Authorization": self._auth_header}
        timeout = aiohttp.ClientTimeout(total=self._timeout)

        _LOGGER.debug("Making %s request to %s", method, endpoint)
        if method == METHOD_POST and json_data:
            _LOGGER.debug("%s request data: %s", method, json_data)

        try:
            async with session.request(
                method,
                url,
                json=json_data,
                headers=headers,
                timeout=timeout,
            ) as response:
                _LOGGER.debug("Response %d from %s", response.status, endpoint)

                if response.status == 401:
                    _LOGGER.error("Authentication failed (401)")
                    raise AirobotAuthError(
                        "Authentication failed - check username/password in "
                        "thermostat menu under 'Mobile app' screen"
                    )
                if response.status == 403:
                    _LOGGER.error("Access forbidden (403)")
                    raise AirobotAuthError(
                        "Access forbidden - ensure Local API is enabled in "
                        "thermostat settings (Connectivity → Local API → Enable)"
                    )
                if response.status >= 400:
                    _LOGGER.warning(
                        "API request failed with status %d for %s",
                        response.status,
                        endpoint,
                    )
                    raise AirobotError(
                        f"API request failed with status {response.status}"
                    )

                response_data = await response.json()
                if not isinstance(response_data, dict):
                    raise AirobotError(
                        f"Unexpected response from {endpoint}: expected a JSON "
                        f"object, got {type(response_data).__name__}"
                    )

                if method == METHOD_POST:
                    _LOGGER.debug("%s response content: %s", method, response_data)

                return response_data

        except TimeoutError as err:
            _LOGGER.warning(
                "Request timeout after %d seconds for %s %s",
                self._timeout,
                method,
                endpoint,
            )
            raise AirobotTimeoutError(
                f"Request to {url} timed out after {self._timeout} seconds"
            ) from err
        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error for %s %s: %s", method, endpoint, err)
            raise AirobotConnectionError(f"Failed to connect to {url}: {err}") from err

    async def get_statuses(self) -> ThermostatStatus:
        """Get all thermostat read-only parameters.

        This method retrieves all current thermostat measurements and status
        information. The thermostat measures air every 30 seconds, which is the
        minimum recommended polling interval.

        Returns:
            ThermostatStatus object with all current measurements and status.

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: For other API errors.
        """
        _LOGGER.debug("Fetching thermostat statuses")
        data = await self._request(METHOD_GET, API_ENDPOINT_GET_STATUSES)
        return ThermostatStatus.from_dict(data)

    async def get_settings(self) -> ThermostatSettings:
        """Get all thermostat configurable settings.

        This method retrieves all thermostat settings that can be read and modified.
        Settings include mode, setpoint temperatures, device name, and various flags.

        Returns:
            ThermostatSettings object with all configurable settings.

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: For other API errors.
        """
        _LOGGER.debug("Fetching thermostat settings")
        data = await self._request(METHOD_GET, API_ENDPOINT_GET_SETTINGS)
        return ThermostatSettings.from_dict(data)

    async def set_settings(self, settings: ThermostatSettings) -> None:
        """Write a full settings object back to the thermostat.

        The transient action flags (REBOOT, RECALIBRATE_CO2) are forced off so
        persisting settings never triggers those actions as a side effect. Use
        reboot_thermostat() or recalibrate_co2_sensor() to trigger them explicitly.
        An empty device name is omitted rather than sent back to the device.

        Args:
            settings: The settings to write to the thermostat.

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails or any value is out of range.
        """
        self._validate_mode(settings.mode)
        self._validate_temperature(settings.setpoint_temp, "HOME temperature")
        self._validate_temperature(settings.setpoint_temp_away, "AWAY temperature")
        self._validate_hysteresis(settings.hysteresis_band)
        if settings.device_name:
            self._validate_device_name(settings.device_name)

        payload = settings.to_dict()
        payload["SETTING_FLAGS"][0]["REBOOT"] = 0
        payload["SETTING_FLAGS"][0]["RECALIBRATE_CO2"] = 0
        if not settings.device_name:
            payload.pop("DEVICE_NAME", None)

        await self._request(METHOD_POST, API_ENDPOINT_SET_SETTINGS, payload)

    def _validate_mode(self, mode: int) -> None:
        """Validate mode value.

        Args:
            mode: Mode value (1=HOME, 2=AWAY).

        Raises:
            AirobotError: If mode is out of valid range.
        """
        if not MODE_MIN <= mode <= MODE_MAX:
            raise AirobotError(
                f"Mode must be between {MODE_MIN} and {MODE_MAX}, got {mode}"
            )

    def _validate_temperature(self, temperature: float, temp_type: str) -> None:
        """Validate temperature value.

        Args:
            temperature: Temperature in °C.
            temp_type: Description of temperature type (for error messages).

        Raises:
            AirobotError: If temperature is out of valid range.
        """
        min_temp = SETPOINT_TEMP_RAW_MIN / 10.0
        max_temp = SETPOINT_TEMP_RAW_MAX / 10.0
        if not min_temp <= temperature <= max_temp:
            raise AirobotError(
                f"{temp_type} must be between {min_temp}°C and {max_temp}°C, "
                f"got {temperature}°C"
            )

    def _validate_hysteresis(self, hysteresis: float) -> None:
        """Validate hysteresis band value.

        Args:
            hysteresis: Hysteresis band in °C.

        Raises:
            AirobotError: If hysteresis is out of valid range.
        """
        min_hyst = HYSTERESIS_BAND_MIN / 10.0
        max_hyst = HYSTERESIS_BAND_MAX / 10.0
        if not min_hyst <= hysteresis <= max_hyst:
            raise AirobotError(
                f"Hysteresis band must be between {min_hyst}°C and {max_hyst}°C, "
                f"got {hysteresis}°C"
            )

    def _validate_device_name(self, name: str) -> None:
        """Validate device name.

        Args:
            name: Device name string.

        Raises:
            AirobotError: If device name is invalid.
        """
        if not isinstance(name, str):
            raise AirobotError(f"Device name must be a string, got {type(name)}")
        if not DEVICE_NAME_MIN_LENGTH <= len(name) <= DEVICE_NAME_MAX_LENGTH:
            raise AirobotError(
                f"Device name length must be between {DEVICE_NAME_MIN_LENGTH} and "
                f"{DEVICE_NAME_MAX_LENGTH} characters, got {len(name)}"
            )

    def _validate_bool_flag(self, value: bool, flag_name: str) -> None:
        """Validate boolean flag value.

        Args:
            value: Boolean flag value.
            flag_name: Name of the flag (for error messages).

        Raises:
            AirobotError: If value is not a boolean.
        """
        if not isinstance(value, bool):
            raise AirobotError(
                f"{flag_name} must be a boolean, got {type(value).__name__}"
            )

    async def _set_partial_settings(self, **kwargs: Any) -> None:
        """Update specific thermostat settings.

        This internal method sends only the specified fields to the API,
        rather than sending all settings.

        Args:
            **kwargs: Setting fields to update (e.g., MODE=2, SETPOINT_TEMP=220).

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails or values are out of range.
        """
        # Build payload with only the specified fields
        payload = dict(kwargs)

        await self._request(METHOD_POST, API_ENDPOINT_SET_SETTINGS, payload)

    async def set_mode(self, mode: ThermostatMode | int) -> None:
        """Set thermostat mode (1=HOME, 2=AWAY).

        Args:
            mode: The mode to set. Accepts a ThermostatMode member
                (ThermostatMode.HOME/ThermostatMode.AWAY) or the raw int
                (1 for HOME, 2 for AWAY).

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails or mode is out of range.
        """
        self._validate_mode(mode)
        await self._set_partial_settings(MODE=int(mode))

    async def set_home_temperature(self, temperature: float) -> None:
        """Set HOME mode setpoint temperature.

        Args:
            temperature: Temperature in °C (range: 5.0°C - 35.0°C).

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails or temperature is out of range.
        """
        self._validate_temperature(temperature, "HOME temperature")
        await self._set_partial_settings(SETPOINT_TEMP=int(temperature * 10))

    async def set_away_temperature(self, temperature: float) -> None:
        """Set AWAY mode setpoint temperature.

        Args:
            temperature: Temperature in °C (range: 5.0°C - 35.0°C).

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails or temperature is out of range.
        """
        self._validate_temperature(temperature, "AWAY temperature")
        await self._set_partial_settings(SETPOINT_TEMP_AWAY=int(temperature * 10))

    async def set_hysteresis_band(self, hysteresis: float) -> None:
        """Set temperature hysteresis band.

        Args:
            hysteresis: Hysteresis in °C (range: 0.0°C - 0.5°C).

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails or hysteresis is out of range.
        """
        self._validate_hysteresis(hysteresis)
        await self._set_partial_settings(HYSTERESIS_BAND=int(hysteresis * 10))

    async def set_device_name(self, name: str) -> None:
        """Set device name.

        Args:
            name: Device name string (1-20 characters).

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails or name is invalid.
        """
        self._validate_device_name(name)
        await self._set_partial_settings(DEVICE_NAME=name)

    async def set_child_lock(self, enabled: bool) -> None:
        """Enable or disable child lock.

        Args:
            enabled: True to enable child lock, False to disable.

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails or enabled is not a boolean.
        """
        self._validate_bool_flag(enabled, "Child lock")
        await self._set_partial_settings(CHILDLOCK_ENABLED=int(enabled))

    async def set_boost_mode(self, enabled: bool) -> None:
        """Enable or disable boost heating mode.

        Args:
            enabled: True to enable boost mode (1 hour), False to disable.

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails or enabled is not a boolean.
        """
        self._validate_bool_flag(enabled, "Boost mode")
        await self._set_partial_settings(BOOST_ENABLED=int(enabled))

    async def reboot_thermostat(self) -> None:
        """Reboot the thermostat.

        Warning: This will restart the thermostat device.

        Rebooting causes the thermostat to drop its TCP connection mid-request,
        so the HTTP call legitimately fails with a connection or timeout error
        even though the reboot command was received and executed. Such errors are
        therefore expected and suppressed here.

        Raises:
            AirobotAuthError: If authentication fails.
        """
        try:
            await self._set_partial_settings(REBOOT=1)
        except (AirobotConnectionError, AirobotTimeoutError):
            _LOGGER.debug(
                "Connection dropped during reboot request, "
                "which is expected as the thermostat restarts"
            )

    async def recalibrate_co2_sensor(self) -> None:
        """Recalibrate CO2 sensor (sets current air as 400 PPM).

        Warning: Only use in clean air environment. CO2 sensor has
        auto-calibration by default - manual calibration rarely needed.

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails.
        """
        await self._set_partial_settings(RECALIBRATE_CO2=1)

    async def toggle_actuator_exercise(self, disabled: bool) -> None:
        """Enable or disable actuator exercise functionality.

        Args:
            disabled: True to disable actuator exercise, False to enable.

        Raises:
            AirobotConnectionError: If connection fails.
            AirobotAuthError: If authentication fails.
            AirobotError: If the request fails or disabled is not a boolean.
        """
        self._validate_bool_flag(disabled, "Actuator exercise disabled")
        await self._set_partial_settings(ACTUATOR_EXERCISE_DISABLED=int(disabled))
