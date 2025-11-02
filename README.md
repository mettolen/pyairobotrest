# pyairobotrest

Python library for controlling [Airobot](https://airobothome.com/) TE1 thermostats via local REST API.

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
    hw_version: int                     # Hardware version
    fw_version: int                     # Firmware version

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
- Home Assistant integration
- Python 3.11, 3.12, 3.13+

## Advanced Usage

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

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines on:

- Setting up your development environment
- Code style and testing requirements
- Submitting pull requests
- Reporting bugs and requesting features

For major changes, please open an issue first to discuss what you would like to change.

## Credits

This library is designed to work with [Airobot](https://airobot.net/) TE1 thermostats and is used by the [Home Assistant Airobot integration](https://www.home-assistant.io/integrations/airobot/).

**Key Features Developed:**

- Complete REST API implementation for Airobot thermostats
- Comprehensive error handling and input validation
- Type-safe API with full asyncio support
- Individual setter methods for granular control
- Production-ready reliability and performance
