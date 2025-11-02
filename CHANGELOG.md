# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- New features that have been added

### Changed

- Changes to existing functionality

### Deprecated

- Features that will be removed in upcoming releases

### Removed

- Features that have been removed

### Fixed

- Bug fixes

### Security

- Security improvements

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
