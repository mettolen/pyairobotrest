# GitHub Copilot Instructions for pyairobotrest

This repository contains `pyairobotrest`, a Python library for controlling [Airobot](https://airobothome.com/) TE1 thermostats via local REST API. It is used by the [Airobot Home Assistant integration](https://www.home-assistant.io/integrations/airobot).

## Project Overview

- **Purpose**: Async Python client for Airobot TE1 thermostats
- **Protocol**: REST API over HTTP (via aiohttp library)
- **Python**: 3.11+
- **Structure**: src layout (`src/pyairobotrest/`)

## Code Standards

### Python Requirements

- **Compatibility**: Python 3.11+
- **Type hints**: Required for all functions, methods, and variables (strict mypy)
- **Async/await**: All I/O operations must be async
- **Docstrings**: Required for all public classes and methods

### Code Style

- **Formatter**: Ruff (line length 88)
- **Linter**: Ruff + mypy (strict mode)
- **Language**: American English for all code, comments, and documentation

### Type Hints

```python
# ✅ Good - comprehensive type hints
async def set_home_temperature(self, temperature: float) -> None:
    """Set the HOME mode target temperature."""

# ✅ Good - Optional fields use | None
temp_air: float | None
```

### Docstrings

```python
# ✅ Good - concise module header
"""Python library for controlling Airobot thermostats."""

# ✅ Good - method docstring with raises
async def get_statuses(self) -> ThermostatStatus:
    """Get current thermostat status and sensor readings.

    Raises:
        AirobotConnectionError: If connection fails.
    """
```

## Architecture

### File Structure

```
src/pyairobotrest/
├── __init__.py      # Public API exports
├── client.py        # AirobotClient - main async REST client
├── const.py         # Constants (ports, limits, API paths, ranges)
├── exceptions.py    # Exception hierarchy
├── models.py        # ThermostatStatus, ThermostatSettings dataclasses
└── py.typed         # PEP-561 marker
```

### Exception Hierarchy

All exceptions inherit from `AirobotError`:

- `AirobotConnectionError` - Connection failures
- `AirobotAuthError` - Authentication errors (401/403)
- `AirobotTimeoutError` - Request timeouts

### Client Patterns

```python
# ✅ Preferred - factory method with pre-initialized session
client = await AirobotClient.create(
    host="192.168.1.100",
    username="T01XXXXXX",
    password="your_password",
)

# ✅ Preferred - context manager
async with AirobotClient(
    host="192.168.1.100",
    username="T01XXXXXX",
    password="your_password",
) as client:
    status = await client.get_statuses()

# Also supported - manual lifecycle
client = AirobotClient(host="192.168.1.100", username="user", password="pass")
status = await client.get_statuses()
await client.close()
```

### Data Models

**`ThermostatStatus`** - Current readings from the thermostat:

- Device info: `device_id`, `hw_version`, `fw_version`
- Sensors: `temp_air`, `hum_air`, `temp_floor` (nullable), `co2` (nullable), `aqi` (nullable)
- State: `status_flags` (`window_open_detected`, `heating_on`)
- Properties: `has_floor_sensor`, `has_co2_sensor`, `has_error`, `is_heating`

**`ThermostatSettings`** - Configurable thermostat settings:

- Mode: `mode` (1=HOME, 2=AWAY)
- Temperatures: `setpoint_temp`, `setpoint_temp_away` (5.0–35.0°C)
- Settings: `hysteresis_band`, `device_name`, `setting_flags`
- Flags: `boost_enabled`, `childlock_enabled`, `reboot`, `actuator_exercise_disabled`, `recalibrate_co2`

### Session Management

- The client can accept an external `aiohttp.ClientSession` (for Home Assistant integration)
- If no session is provided, the client creates and manages its own
- The `_close_session` flag tracks whether the client owns the session
- `close()` only closes sessions the client created

## Development Commands

### Setup

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pyairobotrest --cov-report=term-missing

# Run specific test file
pytest tests/test_client.py -v
```

### Linting

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Ruff linting
ruff check src/pyairobotrest

# Ruff formatting
ruff format src/pyairobotrest

# Type checking
mypy src/pyairobotrest --strict
```

## Best Practices

### ✅ Do

- Use async/await for all HTTP operations
- Wrap aiohttp exceptions in pyairobotrest exceptions
- Use constants from `const.py` for API paths, ranges, and limits
- Add type hints to all function signatures
- Validate inputs before sending to the device
- Write pytest tests for new functionality
- Use `pytest-asyncio` for async test functions
- Process data outside try blocks

### ❌ Don't

- Block the event loop with synchronous I/O
- Expose aiohttp types in the public API
- Use bare `except:` clauses
- Hardcode API paths or value ranges outside `const.py`
- Skip type annotations
- Close sessions that were provided externally

### Error Handling Pattern

```python
# ✅ Good - wrap library exceptions
try:
    response = await self._session.get(url, headers=headers, timeout=timeout)
except TimeoutError as err:
    raise AirobotTimeoutError(f"Timeout connecting to {self._host}") from err
except ClientError as err:
    raise AirobotConnectionError(f"Error connecting to {self._host}") from err

# Process data outside try block
data = await response.json()
return ThermostatStatus.from_dict(data)
```

### Validation Pattern

```python
# ✅ Good - validate before sending
def _validate_temperature(temperature: float) -> None:
    """Validate temperature is within allowed range."""
    if not MIN_TEMPERATURE <= temperature <= MAX_TEMPERATURE:
        raise ValueError(
            f"Temperature must be between {MIN_TEMPERATURE} and {MAX_TEMPERATURE}"
        )
```

### Async Context Manager

```python
# ✅ Good - proper cleanup
async def __aenter__(self) -> Self:
    """Enter async context."""
    return self

async def __aexit__(self, *args: object) -> None:
    """Exit async context."""
    await self.close()
```

## Testing Guidelines

- Use `pytest-asyncio` with `asyncio_mode = "auto"`
- Mock `aiohttp.ClientSession` for unit tests
- Test both success and error paths
- Use parametrized tests for validation edge cases
- Use fixtures for common test setup
- Timeout: 10 seconds per test
- Coverage: minimum 100%

### Test Example

```python
@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    return AsyncMock(spec=aiohttp.ClientSession)

async def test_get_statuses_success(client, mock_session, sample_thermostat_data):
    """Test successful status retrieval."""
    setup_mock_response(mock_session, json_data=sample_thermostat_data)

    status = await client.get_statuses()

    assert status.temp_air is not None
    assert isinstance(status.is_heating, bool)
```

## Constants Reference

Key constants from `const.py`:

| Constant           | Value     | Description                    |
| ------------------ | --------- | ------------------------------ |
| `DEFAULT_PORT`     | 80        | HTTP port                      |
| `DEFAULT_TIMEOUT`  | 10        | Request timeout (seconds)      |
| `MIN_TEMPERATURE`  | 5.0       | Minimum target temp (°C)       |
| `MAX_TEMPERATURE`  | 35.0      | Maximum target temp (°C)       |
| `MIN_HYSTERESIS`   | 0.0       | Minimum hysteresis (°C)        |
| `MAX_HYSTERESIS`   | 0.5       | Maximum hysteresis (°C)        |
| `MODE_HOME`        | 1         | HOME mode value                |
| `MODE_AWAY`        | 2         | AWAY mode value                |
| `MAX_DEVICE_NAME`  | 20        | Maximum device name length     |
