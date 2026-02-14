# pyairobotrest

[![CI](https://github.com/mettolen/pyairobotrest/actions/workflows/ci.yml/badge.svg)](https://github.com/mettolen/pyairobotrest/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/mettolen/pyairobotrest/branch/main/graph/badge.svg)](https://codecov.io/gh/mettolen/pyairobotrest)
[![PyPI version](https://badge.fury.io/py/pyairobotrest.svg)](https://badge.fury.io/py/pyairobotrest)
[![PyPI Downloads](https://img.shields.io/pypi/dm/pyairobotrest.svg)](https://pypi.org/project/pyairobotrest/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyairobotrest.svg)](https://pypi.org/project/pyairobotrest/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python library for controlling [Airobot](https://airobothome.com/) TE1 thermostats via local REST API.

---

This library is used by the [Airobot](https://www.home-assistant.io/integrations/airobot) Home Assistant integration.

<a href="https://www.home-assistant.io/integrations/airobot/" target="_blank"><img alt="Dynamic Regex Badge" src="https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fwww.home-assistant.io%2Fintegrations%2Fairobot%2F&search=(%5B%5Cd%2C%5D%2B)%5Cs*%3C%2Fa%3E%5Cs*active%20installations&replace=%241&style=for-the-badge&logo=homeassistant&label=Active%20installations&labelColor=%23f2f4f9&color=%2346bdf4"></a> <a href="https://www.home-assistant.io/docs/quality_scale/" target="_blank"><img alt="Dynamic Regex Badge" src="https://img.shields.io/badge/dynamic/regex?url=https%3A%2F%2Fwww.home-assistant.io%2Fintegrations%2Fairobot%2F&search=%3Ca%20href%3D'%5B%5E'%5D*quality_scale%5B%5E'%5D*'%3E(%5B%5E%3C%5D%2B%3F)%20quality%3C%2Fa%3E&replace=%241&style=for-the-badge&logo=homeassistant&label=Quality%20scale&labelColor=%23f2f4f9&color=%2346bdf4"></a> <a href="https://my.home-assistant.io/redirect/config_flow_start?domain=airobot" target="_blank"><img alt="Static Badge" src="https://img.shields.io/badge/Airobot-i?style=for-the-badge&logo=homeassistant&label=Add%20integration&labelColor=%23f2f4f9&color=%2346bdf4"></a>

## Features

- 🔌 **Async/await support** using asyncio with comprehensive error handling
- 🌡️ **Temperature control** for HOME and AWAY modes (5-35°C range)
- 🏠 **Mode management** (HOME/AWAY mode switching)
- ⚙️ **Hysteresis control** (0.0-0.5°C range)
- 💨 **Boost mode** for temporary heating (1 hour duration)
- 🔒 **Child lock** control for safety
- 💡 **Sensor monitoring** (temperature, humidity, CO2, AQI)
- 🛡️ **Type hints** for better IDE support and development experience
- ✅ **Input validation** with range checking for all settings
- 📊 **Comprehensive data model** with optional sensor support

## Installation

```bash
pip install pyairobotrest
```

## Prerequisites

Before using this library, ensure your Airobot thermostat is properly configured:

1. **Network Connection**: Connect the thermostat to your local WiFi/Ethernet network
2. **Initial Registration**: Connect to the internet at least once to register with the server and obtain credentials (Device ID and password)
3. **Enable Local API**: In thermostat settings, navigate to "Connectivity → Local API → Enable"
4. **Get Credentials**: Find your Device ID (username) and password in the thermostat menu under "Mobile app" screen

**Note**: After initial setup, internet connectivity is not required for local API access.

## Quick Start

```python
import asyncio
from pyairobotrest import AirobotClient, AirobotConnectionError

async def main():
    # Create client - replace with your thermostat's IP and credentials
    client = AirobotClient(
        host="192.168.1.100",       # or "airobot-thermostat-t01xxxxxx.local"
        username="T01XXXXXX",       # Your thermostat Device ID
        password="your_password"    # Password from "Mobile app" screen
    )

    try:
        # Read current status
        status = await client.get_statuses()
        print(f"Device: {status.device_id}")
        print(f"Hardware: v{status.hw_version_string}")
        print(f"Firmware: v{status.fw_version_string}")
        print(f"Current temperature: {status.temp_air:.1f}°C")
        print(f"Target temperature: {status.setpoint_temp:.1f}°C")
        print(f"Humidity: {status.hum_air:.1f}%")
        print(f"Heating: {'ON' if status.is_heating else 'OFF'}")

        # Check optional sensors
        if status.has_floor_sensor:
            print(f"Floor temperature: {status.temp_floor:.1f}°C")
        if status.has_co2_sensor:
            print(f"CO2: {status.co2} ppm (AQI: {status.aqi})")

        # Read current settings
        settings = await client.get_settings()
        print(f"Mode: {'HOME' if settings.mode == 1 else 'AWAY'}")
        print(f"HOME temp: {settings.setpoint_temp}°C")
        print(f"AWAY temp: {settings.setpoint_temp_away}°C")

        # Control the thermostat
        await client.set_home_temperature(23.0)  # Set HOME temperature
        await client.set_mode(1)                 # Switch to HOME mode
        await client.set_boost_mode(True)        # Enable boost for 1 hour

    except AirobotConnectionError as err:
        print(f"Connection error: {err}")
    finally:
        await client.close()

asyncio.run(main())
```

## Context Manager Usage (Recommended)

```python
import asyncio
from pyairobotrest import AirobotClient

async def main():
    try:
        # Using async context manager automatically handles connection cleanup
        async with AirobotClient(
            host="192.168.1.100",
            username="T01XXXXXX",
            password="your_password"
        ) as client:
            # Read status
            status = await client.get_statuses()
            print(f"Temperature: {status.temp_air:.1f}°C")
            print(f"Heating: {status.is_heating}")

            # Configure thermostat
            await client.set_home_temperature(22.5)
            await client.set_hysteresis_band(0.3)
            await client.set_child_lock(True)

    except Exception as err:
        print(f"Error: {err}")

asyncio.run(main())
```

## Factory Method (Recommended for Home Assistant)

For explicit session initialization, use the factory method pattern:

```python
import asyncio
from pyairobotrest import AirobotClient

async def main():
    # Factory method ensures session is initialized before use
    client = await AirobotClient.create(
        host="192.168.1.100",
        username="T01XXXXXX",
        password="your_password"
    )

    try:
        status = await client.get_statuses()
        print(f"Temperature: {status.temp_air:.1f}°C")
    finally:
        await client.close()

asyncio.run(main())
```

## API Reference

### Client Initialization

| Method                   | Description                                 | Returns       |
| ------------------------ | ------------------------------------------- | ------------- |
| `AirobotClient()`        | Standard constructor                        | AirobotClient |
| `AirobotClient.create()` | Factory method with session pre-initialized | AirobotClient |

### Main Client Methods

| Method                               | Description                   | Parameters                   |
| ------------------------------------ | ----------------------------- | ---------------------------- |
| `get_statuses()`                     | Read all current measurements | None                         |
| `get_settings()`                     | Read all thermostat settings  | None                         |
| `set_mode(mode)`                     | Set HOME/AWAY mode            | `mode: int` (1=HOME, 2=AWAY) |
| `set_home_temperature(temp)`         | Set HOME temperature          | `temp: float` (5.0-35.0°C)   |
| `set_away_temperature(temp)`         | Set AWAY temperature          | `temp: float` (5.0-35.0°C)   |
| `set_hysteresis_band(hyst)`          | Set temperature hysteresis    | `hyst: float` (0.0-0.5°C)    |
| `set_device_name(name)`              | Set device name               | `name: str` (1-20 chars)     |
| `set_child_lock(enabled)`            | Enable/disable child lock     | `enabled: bool`              |
| `set_boost_mode(enabled)`            | Enable/disable boost mode     | `enabled: bool`              |
| `reboot_thermostat()`                | Reboot the thermostat         | None                         |
| `recalibrate_co2_sensor()`           | Recalibrate CO2 sensor        | None                         |
| `toggle_actuator_exercise(disabled)` | Enable/disable actuator test  | `disabled: bool`             |

### Data Model (ThermostatStatus)

```python
@dataclass
class ThermostatStatus:
    # Device identification
    device_id: str                      # Unique device ID
    hw_version: int                     # Hardware version (raw)
    fw_version: int                     # Firmware version (raw)

    # Temperature measurements
    temp_air: float                     # Air temperature in °C
    temp_floor: float | None            # Floor temperature in °C (None if not attached)
    setpoint_temp: float                # Target temperature in °C

    # Environmental sensors
    hum_air: float                      # Relative humidity in %
    co2: int | None                     # CO2 in ppm (None if not equipped)
    aqi: int | None                     # Air quality index 0-5 (None if no CO2)

    # Status
    is_heating: bool                    # True if actively heating
    has_error: bool                     # True if error present
    error_code: int                     # Error code (0 = no error)
    uptime: int                         # Device uptime in seconds

    # Sensor availability
    has_floor_sensor: bool              # True if floor sensor attached
    has_co2_sensor: bool                # True if CO2 sensor equipped

    # Version properties (human-readable)
    hw_version_string: str              # Hardware version (e.g., "1.11")
    fw_version_string: str              # Firmware version (e.g., "1.11")
```

### Data Model (ThermostatSettings)

```python
@dataclass
class ThermostatSettings:
    device_id: str                      # Unique device ID
    mode: int                           # 1=HOME, 2=AWAY
    setpoint_temp: float                # HOME temperature in °C
    setpoint_temp_away: float           # AWAY temperature in °C
    hysteresis_band: float              # Temperature hysteresis in °C
    device_name: str                    # Device name (1-20 characters)

    # Setting flags
    setting_flags: SettingFlags
        childlock_enabled: bool         # Child lock status
        boost_enabled: bool             # Boost mode status (1 hour)
        reboot: bool                    # Reboot flag
        recalibrate_co2: bool           # CO2 calibration flag
        actuator_exercise_disabled: bool # Actuator exercise status
```

### Exception Handling

```python
from pyairobotrest import (
    AirobotConnectionError,     # Connection issues
    AirobotAuthError,           # Authentication failures
    AirobotTimeoutError,        # Timeout errors
    AirobotError,               # General API errors
)

try:
    async with AirobotClient("192.168.1.100", "T01XXXXXX", "password") as client:
        status = await client.get_statuses()
except AirobotAuthError:
    print("Authentication failed - check username/password")
except AirobotConnectionError:
    print("Failed to connect to thermostat")
except AirobotTimeoutError:
    print("Operation timed out")
except AirobotError as err:
    print(f"API error: {err}")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/mettolen/pyairobotrest.git
cd pyairobotrest

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Testing & Quality

```bash
# Run all tests with coverage
pytest --cov=pyairobotrest --cov-report=term-missing

# Run type checking
mypy src/pyairobotrest

# Run linting and formatting
ruff check src/pyairobotrest
ruff format src/pyairobotrest

# Run pre-commit hooks (if installed)
pre-commit run --all-files
```

## Requirements

- Python 3.11+
- Dependencies:
  - `aiohttp` >= 3.9.0 (HTTP client for REST API communication)
  - `asyncio` (built-in, async/await support)

## Compatibility

This library is tested and compatible with:

- Airobot TE1 thermostats with local REST API enabled
  - Tested with hardware v1.1 (257) and firmware v1.11 (267)
- Home Assistant integration
- Python 3.11, 3.12, 3.13+

## Advanced Usage

### Firmware and Hardware Version Decoding

The thermostat reports firmware and hardware versions as encoded integers. The library automatically decodes these to human-readable strings:

```python
status = await client.get_statuses()

# Raw version numbers (as stored in device)
print(f"Raw HW version: {status.hw_version}")  # e.g., 267
print(f"Raw FW version: {status.fw_version}")  # e.g., 257

# Human-readable version strings (automatically decoded)
print(f"HW version: v{status.hw_version_string}")  # e.g., v1.11
print(f"FW version: v{status.fw_version_string}")  # e.g., v1.1

# Version encoding: value = major * 256 + minor
# Example: 267 = 1 * 256 + 11 = v1.11
#          257 = 1 * 256 + 1  = v1.1
```

### Input Validation

All setter methods validate input values before sending to the API:

```python
# These will raise AirobotError before making API calls
await client.set_home_temperature(40.0)   # Error: outside 5-35°C range
await client.set_hysteresis_band(1.0)     # Error: outside 0-0.5°C range
await client.set_device_name("x" * 25)    # Error: name too long (max 20 chars)
await client.set_mode(3)                  # Error: invalid mode (must be 1 or 2)
```

### Strict Validation Mode

For testing or strict data validation scenarios, enable strict mode to raise exceptions for out-of-range sensor values:

```python
from pyairobotrest.models import ThermostatStatus

# Normal mode (default): logs warnings for out-of-range values
status = ThermostatStatus.from_dict(api_response_data)

# Strict mode: raises ValueError for out-of-range values
try:
    status = ThermostatStatus.from_dict(api_response_data, strict=True)
except ValueError as e:
    print(f"Invalid sensor data: {e}")
```

**Use cases for strict mode:**

- Unit testing with known good data
- Development and debugging
- Data quality validation pipelines

**Default mode (strict=False) is recommended for production** as it handles edge cases gracefully by logging warnings.

### Polling Best Practices

The thermostat measures air every 30 seconds, which is the minimum recommended polling interval:

```python
import asyncio

async def monitor_temperature():
    async with AirobotClient("192.168.1.100", "T01XXXXXX", "password") as client:
        while True:
            status = await client.get_statuses()
            print(f"Temperature: {status.temp_air:.1f}°C")
            await asyncio.sleep(30)  # Poll every 30 seconds
```

## Troubleshooting

### Connection Issues

1. **Check IP address**: Ensure the thermostat IP is correct
2. **Local API enabled**: Verify "Connectivity - Local API – Enable" is turned on
3. **Network connectivity**: Ensure the thermostat is on the same network
4. **Credentials**: Check username (Device ID) and password from "Mobile app" screen

### Common Error Patterns

```python
# Handle specific error types
try:
    await client.get_statuses()
except AirobotAuthError:
    print("Authentication failed - check credentials")
except AirobotTimeoutError:
    print("Request timed out - thermostat may be offline")
except AirobotConnectionError as err:
    if "refused" in str(err).lower():
        print("Connection refused - check IP and ensure local API is enabled")
    else:
        print(f"Connection error: {err}")
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Setting up your development environment
- Code style and testing requirements
- Submitting pull requests
- Reporting bugs and requesting features

For major changes, please open an issue first to discuss what you would like to change.
