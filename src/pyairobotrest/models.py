"""Data models for pyairobotrest."""

import logging
from dataclasses import dataclass
from typing import Any

from .const import (
    AQI_MAX,
    AQI_MIN,
    CO2_MAX,
    CO2_MIN,
    DEVICE_NAME_MAX_LENGTH,
    DEVICE_NAME_MIN_LENGTH,
    FLAG_MAX,
    FLAG_MIN,
    FW_VERSION_MAX,
    FW_VERSION_MIN,
    HUM_AIR_MAX,
    HUM_AIR_MIN,
    HW_VERSION_MAX,
    HW_VERSION_MIN,
    HYSTERESIS_BAND_MAX,
    HYSTERESIS_BAND_MIN,
    INT16_SENSOR_NOT_ATTACHED,
    MODE_MAX,
    MODE_MIN,
    SETPOINT_TEMP_AWAY_RAW_MAX,
    SETPOINT_TEMP_AWAY_RAW_MIN,
    SETPOINT_TEMP_MAX,
    SETPOINT_TEMP_MIN,
    SETPOINT_TEMP_RAW_MAX,
    SETPOINT_TEMP_RAW_MIN,
    TEMP_AIR_MAX,
    TEMP_AIR_MIN,
    TEMP_FLOOR_MAX,
    TEMP_FLOOR_MIN,
    UINT16_SENSOR_NOT_ATTACHED,
    UPTIME_MAX,
    UPTIME_MIN,
)

_LOGGER = logging.getLogger(__name__)
_LOGGER.addHandler(logging.NullHandler())


def _validate_range(
    value: float | int | None,
    min_val: float | int,
    max_val: float | int,
    name: str,
    strict: bool = False,
) -> None:
    """Validate value is within expected range.

    Args:
        value: Value to validate.
        min_val: Minimum allowed value.
        max_val: Maximum allowed value.
        name: Parameter name for error messages.
        strict: If True, raise exception instead of logging warning.

    Raises:
        ValueError: If strict=True and value is out of range.
    """
    if value is not None and not min_val <= value <= max_val:
        message = (
            f"Parameter {name} value {value} is outside expected range "
            f"[{min_val}, {max_val}]"
        )
        if strict:
            raise ValueError(message)
        _LOGGER.warning(message)


@dataclass
class StatusFlags:
    """Status flags model."""

    window_open_detected: bool
    heating_on: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StatusFlags":
        """Create StatusFlags from dictionary."""
        return cls(
            window_open_detected=bool(data.get("WINDOW_OPEN_DETECTED", 0)),
            heating_on=bool(data.get("HEATING_ON", 0)),
        )


@dataclass
class ThermostatStatus:
    """Thermostat status model containing all read-only parameters."""

    device_id: str
    hw_version: int
    fw_version: int
    temp_air: float | None  # Air temperature in °C, None if sensor not attached
    hum_air: float | None  # Relative humidity in %, None if sensor not attached
    temp_floor: float | None  # Floor temperature in °C, None if sensor not attached
    co2: int | None  # CO2 measurement in ppm, None if sensor not equipped
    aqi: int | None  # Air quality index (0-5), None if CO2 sensor not equipped
    device_uptime: int  # Device uptime in seconds
    heating_uptime: int  # Heating uptime in seconds
    errors: int  # Error code, 0 means no error
    setpoint_temp: float  # Setpoint temperature in °C
    status_flags: StatusFlags

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], strict: bool = False
    ) -> "ThermostatStatus":
        """Create ThermostatStatus from API response dictionary.

        Args:
            data: Dictionary containing API response data.
            strict: If True, raise ValueError for out-of-range values instead of
                logging warnings. Useful for testing or strict validation scenarios.

        Returns:
            ThermostatStatus instance.

        Raises:
            ValueError: If strict=True and any value is outside expected range.
        """
        # Convert temperature values from API format (0.1°C units) to °C
        temp_air_raw = data.get("TEMP_AIR", INT16_SENSOR_NOT_ATTACHED)
        temp_air = (
            None if temp_air_raw == INT16_SENSOR_NOT_ATTACHED else temp_air_raw / 10.0
        )
        temp_floor_raw = data.get("TEMP_FLOOR", INT16_SENSOR_NOT_ATTACHED)
        temp_floor = (
            None
            if temp_floor_raw == INT16_SENSOR_NOT_ATTACHED
            else temp_floor_raw / 10.0
        )
        setpoint_temp = data.get("SETPOINT_TEMP", 200) / 10.0

        # Convert humidity from API format (0.1% units) to %
        hum_air_raw = data.get("HUM_AIR", UINT16_SENSOR_NOT_ATTACHED)
        hum_air = (
            None if hum_air_raw == UINT16_SENSOR_NOT_ATTACHED else hum_air_raw / 10.0
        )

        # Handle CO2 and AQI (None if sensor not equipped)
        co2_raw = data.get("CO2", UINT16_SENSOR_NOT_ATTACHED)
        co2 = None if co2_raw == UINT16_SENSOR_NOT_ATTACHED else co2_raw
        aqi = data.get("AQI") if co2 is not None else None

        # Parse status flags
        status_flags_list = data.get("STATUS_FLAGS", [{}])
        status_flags_data = status_flags_list[0] if status_flags_list else {}
        status_flags = StatusFlags.from_dict(status_flags_data)

        # Extract remaining values for validation (convert to int if string)
        hw_version_raw = data.get("HW_VERSION", 0)
        fw_version_raw = data.get("FW_VERSION", 0)
        device_uptime_raw = data.get("DEVICE_UPTIME", 0)
        heating_uptime_raw = data.get("HEATING_UPTIME", 0)
        errors_raw = data.get("ERRORS", 0)

        # Convert string values to integers
        hw_version = int(hw_version_raw) if hw_version_raw != 0 else 0
        fw_version = int(fw_version_raw) if fw_version_raw != 0 else 0
        device_uptime = int(device_uptime_raw) if device_uptime_raw != 0 else 0
        heating_uptime = int(heating_uptime_raw) if heating_uptime_raw != 0 else 0
        errors = int(errors_raw) if errors_raw != 0 else 0

        # Validate all values against expected ranges
        _validate_range(
            hw_version, HW_VERSION_MIN, HW_VERSION_MAX, "HW_VERSION", strict
        )
        _validate_range(
            fw_version, FW_VERSION_MIN, FW_VERSION_MAX, "FW_VERSION", strict
        )
        _validate_range(temp_air, TEMP_AIR_MIN, TEMP_AIR_MAX, "TEMP_AIR", strict)
        _validate_range(hum_air, HUM_AIR_MIN, HUM_AIR_MAX, "HUM_AIR", strict)
        _validate_range(
            temp_floor, TEMP_FLOOR_MIN, TEMP_FLOOR_MAX, "TEMP_FLOOR", strict
        )
        _validate_range(co2, CO2_MIN, CO2_MAX, "CO2", strict)
        _validate_range(aqi, AQI_MIN, AQI_MAX, "AQI", strict)
        _validate_range(
            setpoint_temp, SETPOINT_TEMP_MIN, SETPOINT_TEMP_MAX, "SETPOINT_TEMP", strict
        )
        _validate_range(device_uptime, UPTIME_MIN, UPTIME_MAX, "DEVICE_UPTIME", strict)
        _validate_range(
            heating_uptime, UPTIME_MIN, UPTIME_MAX, "HEATING_UPTIME", strict
        )

        return cls(
            device_id=data.get("DEVICE_ID", ""),
            hw_version=hw_version,
            fw_version=fw_version,
            temp_air=temp_air,
            hum_air=hum_air,
            temp_floor=temp_floor,
            co2=co2,
            aqi=aqi,
            device_uptime=device_uptime,
            heating_uptime=heating_uptime,
            errors=errors,
            setpoint_temp=setpoint_temp,
            status_flags=status_flags,
        )

    @property
    def has_floor_sensor(self) -> bool:
        """Return True if floor sensor is attached."""
        return self.temp_floor is not None

    @property
    def has_co2_sensor(self) -> bool:
        """Return True if CO2 sensor is equipped."""
        return self.co2 is not None

    @property
    def has_error(self) -> bool:
        """Return True if thermostat has an error."""
        return self.errors > 0

    @property
    def is_heating(self) -> bool:
        """Return True if heating is currently active."""
        return self.status_flags.heating_on


@dataclass
class SettingFlags:
    """Setting flags model for configurable thermostat flags."""

    reboot: bool
    actuator_exercise_disabled: bool
    recalibrate_co2: bool
    childlock_enabled: bool
    boost_enabled: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SettingFlags":
        """Create SettingFlags from dictionary."""
        return cls(
            reboot=bool(int(data.get("REBOOT", 0))),
            actuator_exercise_disabled=bool(
                int(data.get("ACTUATOR_EXERCISE_DISABLED", 0))
            ),
            recalibrate_co2=bool(int(data.get("RECALIBRATE_CO2", 0))),
            childlock_enabled=bool(int(data.get("CHILDLOCK_ENABLED", 0))),
            boost_enabled=bool(int(data.get("BOOST_ENABLED", 0))),
        )

    def to_dict(self) -> dict[str, int]:
        """Convert SettingFlags to dictionary format for API."""
        return {
            "REBOOT": int(self.reboot),
            "ACTUATOR_EXERCISE_DISABLED": int(self.actuator_exercise_disabled),
            "RECALIBRATE_CO2": int(self.recalibrate_co2),
            "CHILDLOCK_ENABLED": int(self.childlock_enabled),
            "BOOST_ENABLED": int(self.boost_enabled),
        }


@dataclass
class ThermostatSettings:
    """Thermostat settings model containing all configurable parameters."""

    device_id: str  # Read-only
    mode: int  # 1=HOME, 2=AWAY
    setpoint_temp: float  # Setpoint temperature in HOME mode (°C)
    setpoint_temp_away: float  # Setpoint temperature in AWAY mode (°C)
    hysteresis_band: float  # Hysteresis for heating (°C)
    device_name: str  # Thermostat name
    setting_flags: SettingFlags

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], strict: bool = False
    ) -> "ThermostatSettings":
        """Create ThermostatSettings from API response dictionary.

        Args:
            data: Dictionary containing API response data.
            strict: If True, raise ValueError for out-of-range values instead of
                logging warnings. Useful for testing or strict validation scenarios.

        Returns:
            ThermostatSettings instance.

        Raises:
            ValueError: If strict=True and any value is outside expected range.
        """
        # Convert temperature values from API format (0.1°C units) to °C
        setpoint_temp_raw = data.get("SETPOINT_TEMP", 220)
        setpoint_temp_away_raw = data.get("SETPOINT_TEMP_AWAY", 180)
        hysteresis_band_raw = data.get("HYSTERESIS_BAND", 1)

        # Convert string values to integers (handle real API responses)
        setpoint_temp = int(setpoint_temp_raw) / 10.0
        setpoint_temp_away = int(setpoint_temp_away_raw) / 10.0
        hysteresis_band = int(hysteresis_band_raw) / 10.0

        # Parse setting flags
        setting_flags_list = data.get("SETTING_FLAGS", [{}])
        setting_flags_data = setting_flags_list[0] if setting_flags_list else {}
        setting_flags = SettingFlags.from_dict(setting_flags_data)

        # Extract mode and convert to int if string
        mode_raw = data.get("MODE", 1)
        mode = int(mode_raw) if mode_raw != 0 else 1

        # Validate values against expected ranges
        _validate_range(mode, MODE_MIN, MODE_MAX, "MODE", strict)
        _validate_range(
            setpoint_temp * 10,
            SETPOINT_TEMP_RAW_MIN,
            SETPOINT_TEMP_RAW_MAX,
            "SETPOINT_TEMP",
            strict,
        )
        _validate_range(
            setpoint_temp_away * 10,
            SETPOINT_TEMP_AWAY_RAW_MIN,
            SETPOINT_TEMP_AWAY_RAW_MAX,
            "SETPOINT_TEMP_AWAY",
            strict,
        )
        _validate_range(
            hysteresis_band * 10,
            HYSTERESIS_BAND_MIN,
            HYSTERESIS_BAND_MAX,
            "HYSTERESIS_BAND",
            strict,
        )

        device_name = data.get("DEVICE_NAME", "")
        # Note: API often returns empty device name, which appears to be normal behavior
        # Only warn/error if name is present but invalid length
        if device_name and (
            len(device_name) < DEVICE_NAME_MIN_LENGTH
            or len(device_name) > DEVICE_NAME_MAX_LENGTH
        ):
            message = (
                f"Parameter DEVICE_NAME length {len(device_name)} is outside "
                f"expected range [{DEVICE_NAME_MIN_LENGTH}, {DEVICE_NAME_MAX_LENGTH}]"
            )
            if strict:
                raise ValueError(message)
            _LOGGER.warning(message)

        # Validate flag values
        for flag_name, flag_value in setting_flags.to_dict().items():
            _validate_range(flag_value, FLAG_MIN, FLAG_MAX, flag_name, strict)

        return cls(
            device_id=data.get("DEVICE_ID", ""),
            mode=mode,
            setpoint_temp=setpoint_temp,
            setpoint_temp_away=setpoint_temp_away,
            hysteresis_band=hysteresis_band,
            device_name=device_name,
            setting_flags=setting_flags,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert ThermostatSettings to dictionary format for API requests.

        Note: DEVICE_ID is excluded as it's a read-only field and should not be
        sent in API requests.
        """
        return {
            "MODE": self.mode,
            "SETPOINT_TEMP": int(self.setpoint_temp * 10),  # Convert to 0.1°C units
            "SETPOINT_TEMP_AWAY": int(
                self.setpoint_temp_away * 10
            ),  # Convert to 0.1°C units
            "HYSTERESIS_BAND": int(self.hysteresis_band * 10),  # Convert to 0.1°C units
            "DEVICE_NAME": self.device_name,
            "SETTING_FLAGS": [self.setting_flags.to_dict()],
        }

    @property
    def is_home_mode(self) -> bool:
        """Return True if thermostat is in HOME mode."""
        return self.mode == 1

    @property
    def is_away_mode(self) -> bool:
        """Return True if thermostat is in AWAY mode."""
        return self.mode == 2
