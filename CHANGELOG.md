# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-07-09

### Added

- `ThermostatMode` `IntEnum` (`HOME`, `AWAY`) exported from the package. `set_mode()` now accepts a `ThermostatMode` member in addition to the raw `int`.
- `AirobotClient.set_settings()` to write a full `ThermostatSettings` object back to the thermostat. Transient action flags (`REBOOT`, `RECALIBRATE_CO2`) are forced off so persisting settings never triggers those actions as a side effect, and an empty device name is omitted from the request.

### Changed

- `ThermostatStatus.from_dict()` now coerces all numeric fields (temperatures, humidity, CO2, AQI) to their expected types before use, matching `ThermostatSettings.from_dict()`. This prevents `TypeError`/type mismatches when the device returns numeric values as strings.
- Raised the `HW_VERSION`/`FW_VERSION` validation ceiling from `999` to `65535` (uint16 max) so valid versions above `3.231` are no longer flagged as out of range.
- Status and settings parsing now share the same default fallbacks via the `SETPOINT_TEMP_RAW_DEFAULT`, `SETPOINT_TEMP_AWAY_RAW_DEFAULT`, and `HYSTERESIS_BAND_DEFAULT` constants, removing an inconsistent `SETPOINT_TEMP` default.

### Fixed

- `reboot_thermostat()` no longer raises when the thermostat drops its TCP connection mid-request while restarting; the resulting `AirobotConnectionError` and `AirobotTimeoutError` are now expected and suppressed, since the reboot command was received and executed. Authentication errors are still raised.
- Missing `HW_VERSION`/`FW_VERSION` fields no longer emit a spurious out-of-range warning on every poll.
- Requests now raise `AirobotError` when the API returns a non-object (e.g. a JSON array) instead of silently returning an unexpected type.

## [0.3.0] - 2026-01-24

### Added

- Human-readable version properties `hw_version_string` and `fw_version_string` on `ThermostatStatus` (decodes raw firmware/hardware versions from format: major \* 256 + minor)
- Enhanced logging capabilities with comprehensive debug and error logging throughout the client
- NullHandler to prevent logging warnings when library is used without logging configuration
- Complete type annotations for all test files and example.py
- New test modules: `test_models.py`, `test_factory_and_validation.py`, `test_setters.py`
- Pre-commit hook for mypy now runs on both `src/` and `tests/` directories

### Changed

- Reorganized and consolidated test files using parametrized tests
- Updated mypy pre-commit configuration to include pytest as additional dependency
- Fixed codecov GitHub Actions configuration (`file:` → `files:`)

### Fixed

- All mypy strict type checking errors (55 errors resolved)
- Added proper type hints for function parameters and return types across test suite

## [0.2.0] - 2026-01-02

### Changed

- **BREAKING**: Renamed `FLOOR_SENSOR_NOT_ATTACHED` constant to `INT16_SENSOR_NOT_ATTACHED` and `CO2_SENSOR_NOT_EQUIPPED` constant to `UINT16_SENSOR_NOT_ATTACHED` to make data types explicit
- `temp_air` and `temp_floor` fields in `ThermostatStatus` now return `None` when sensor value equals `INT16_SENSOR_NOT_ATTACHED` (32767)
- `co2` and `hum_air` fields in `ThermostatStatus` now return `None` when sensor value equals `UINT16_SENSOR_NOT_ATTACHED` (65535)
- Updated type hints: `temp_air`, `hum_air`, `temp_floor`, and `co2` are now `float | None` or `int | None` instead of `float` or `int`
- Replaced `asyncio.timeout` with aiohttp's native `ClientTimeout` for more idiomatic and efficient timeout handling

### Added

- Test coverage for air temperature sensor not attached scenario
- Test coverage for humidity sensor not attached scenario

## [0.1.0] - 2025-10-30

### Added

- Initial release of pyairobotrest
- Async client for Airobot thermostat controllers
- Support for all controller features:
  - Temperature control (HOME, AWAY, ANTIFREEZE modes)
  - Fan speed control (5 levels)
  - Device power management
  - Child lock functionality
  - Light control
  - Hysteresis band adjustment
  - Device naming
- Comprehensive input validation with min/max range checking
- Individual setting update methods (partial updates)
- Full type hints support (py.typed)
- Extensive error handling with specific exceptions
- Polling and monitoring capabilities

### Dependencies

- aiohttp >= 3.8.0

[Unreleased]: https://github.com/mettolen/pyairobotrest/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/mettolen/pyairobotrest/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/mettolen/pyairobotrest/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mettolen/pyairobotrest/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mettolen/pyairobotrest/releases/tag/v0.1.0
