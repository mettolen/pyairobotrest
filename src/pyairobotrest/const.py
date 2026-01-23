"""Constants for pyairobotrest."""

__all__ = [
    # API endpoints
    "API_BASE_PATH",
    "API_ENDPOINT_GET_STATUSES",
    "API_ENDPOINT_GET_SETTINGS",
    "API_ENDPOINT_SET_SETTINGS",
    # Default values
    "DEFAULT_TIMEOUT",
    "DEFAULT_PORT",
    "POLLING_INTERVAL",
    # HTTP methods
    "METHOD_GET",
    "METHOD_POST",
    # Value constants
    "INT16_SENSOR_NOT_ATTACHED",
    "UINT16_SENSOR_NOT_ATTACHED",
    "MIN_TEMP_RAW",
    "MAX_TEMP_RAW",
    "NO_ERROR",
    # Validation ranges
    "TEMP_AIR_MIN",
    "TEMP_AIR_MAX",
    "TEMP_FLOOR_MIN",
    "TEMP_FLOOR_MAX",
    "SETPOINT_TEMP_MIN",
    "SETPOINT_TEMP_MAX",
    "HUM_AIR_MIN",
    "HUM_AIR_MAX",
    "CO2_MIN",
    "CO2_MAX",
    "AQI_MIN",
    "AQI_MAX",
    "HW_VERSION_MIN",
    "HW_VERSION_MAX",
    "FW_VERSION_MIN",
    "FW_VERSION_MAX",
    "UPTIME_MIN",
    "UPTIME_MAX",
    # Settings validation ranges
    "MODE_MIN",
    "MODE_MAX",
    "MODE_HOME",
    "MODE_AWAY",
    "SETPOINT_TEMP_RAW_MIN",
    "SETPOINT_TEMP_RAW_MAX",
    "SETPOINT_TEMP_RAW_DEFAULT",
    "SETPOINT_TEMP_AWAY_RAW_MIN",
    "SETPOINT_TEMP_AWAY_RAW_MAX",
    "SETPOINT_TEMP_AWAY_RAW_DEFAULT",
    "HYSTERESIS_BAND_MIN",
    "HYSTERESIS_BAND_MAX",
    "HYSTERESIS_BAND_DEFAULT",
    "DEVICE_NAME_MIN_LENGTH",
    "DEVICE_NAME_MAX_LENGTH",
    "FLAG_MIN",
    "FLAG_MAX",
]

# API endpoints
API_BASE_PATH = "/api/thermostat"
API_ENDPOINT_GET_STATUSES = "/getStatuses"
API_ENDPOINT_GET_SETTINGS = "/getSettings"
API_ENDPOINT_SET_SETTINGS = "/setSettings"

# Default values
DEFAULT_TIMEOUT = 10
DEFAULT_PORT = 80
POLLING_INTERVAL = 30  # Minimum recommended polling interval in seconds

# HTTP methods
METHOD_GET = "GET"
METHOD_POST = "POST"

# Value constants
INT16_SENSOR_NOT_ATTACHED = 32767  # Signed 16-bit max (temperature sensors)
UINT16_SENSOR_NOT_ATTACHED = 65535  # Unsigned 16-bit max (CO2/humidity sensors)

# Temperature limits (in 0.1°C units as per API)
MIN_TEMP_RAW = 50  # 5.0°C
MAX_TEMP_RAW = 350  # 35.0°C

# Error status
NO_ERROR = 0

# Validation ranges (reasonable sensor ranges)
# Temperature ranges (°C)
TEMP_AIR_MIN = -40.0  # Reasonable air temperature minimum
TEMP_AIR_MAX = 80.0  # Reasonable air temperature maximum
TEMP_FLOOR_MIN = -40.0  # Reasonable floor temperature minimum
TEMP_FLOOR_MAX = 80.0  # Reasonable floor temperature maximum
SETPOINT_TEMP_MIN = 5.0  # Minimum setpoint temperature
SETPOINT_TEMP_MAX = 35.0  # Maximum setpoint temperature

# Humidity range (%)
HUM_AIR_MIN = 0.0
HUM_AIR_MAX = 100.0  # Maximum relative humidity

# CO2 range (ppm)
CO2_MIN = 0
CO2_MAX = 10000  # Reasonable CO2 maximum (indoor air quality)

# Air Quality Index range
AQI_MIN = 0
AQI_MAX = 5

# Version ranges
HW_VERSION_MIN = 256
HW_VERSION_MAX = 999
FW_VERSION_MIN = 256
FW_VERSION_MAX = 999

# Uptime range (seconds)
UPTIME_MIN = 0
UPTIME_MAX = 4294967295  # uint32 max

# Settings validation ranges
# Mode range
MODE_MIN = 1  # HOME mode
MODE_MAX = 2  # AWAY mode
MODE_HOME = 1
MODE_AWAY = 2

# Setpoint temperature ranges (in 0.1°C units as per API)
# Both HOME and AWAY temperatures have same range: 50-350 (5.0°C - 35.0°C)
SETPOINT_TEMP_RAW_MIN = 50  # 5.0°C
SETPOINT_TEMP_RAW_MAX = 350  # 35.0°C
SETPOINT_TEMP_RAW_DEFAULT = 220  # 22.0°C default for HOME mode

SETPOINT_TEMP_AWAY_RAW_MIN = 50  # 5.0°C (same as HOME)
SETPOINT_TEMP_AWAY_RAW_MAX = 350  # 35.0°C (same as HOME)
SETPOINT_TEMP_AWAY_RAW_DEFAULT = 180  # 18.0°C default for AWAY mode

# Hysteresis band range (in 0.1°C units)
HYSTERESIS_BAND_MIN = 0  # 0.0°C
HYSTERESIS_BAND_MAX = 5  # 0.5°C
HYSTERESIS_BAND_DEFAULT = 1  # 0.1°C default

# Device name length
DEVICE_NAME_MIN_LENGTH = 1
DEVICE_NAME_MAX_LENGTH = 20

# Boolean flag ranges
FLAG_MIN = 0
FLAG_MAX = 1
