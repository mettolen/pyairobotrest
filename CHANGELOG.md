# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[Unreleased]: https://github.com/mettolen/pyairobotrest/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mettolen/pyairobotrest/releases/tag/v0.1.0
