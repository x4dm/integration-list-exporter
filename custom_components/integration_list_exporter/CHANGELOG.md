# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2024-12-14

### Fixed
- Fixed deprecation warning for `is_hassio` import - now uses `homeassistant.helpers.hassio.is_hassio` instead of deprecated `homeassistant.components.hassio.is_hassio`
- Fixed blocking I/O operation warning - file writes now use async executor to avoid blocking the event loop

## [1.1.0] - 2024-12-14

### Added
- Version numbers now shown for all integrations (core integrations show Home Assistant version, custom integrations show their specific version)
- New Add-ons section listing all installed add-ons with version numbers
- Enhanced system information including:
  - Supervisor status (true/false)
  - Docker status (true/false)
  - User root status (true/false)
  - Virtual environment detection (true/false)
  - Operating system family and version
  - CPU architecture (e.g., aarch64)
  - Host operating system (e.g., Home Assistant OS 16.3)
  - Supervisor update channel (e.g., stable)
  - Supervisor version
  - Agent version
  - Docker version
  - Disk total and used (in GB)
  - Disk health status (true/false)
  - Board type (e.g., rpi4-64)

### Removed
- Timezone information from system output
- Latitude and longitude from system output

## [1.0.0] - 2024-12-14

### Added
- Initial release
- Daily automatic export of all integrations to CSV file
- System information section with Home Assistant version, Python version, installation type, and config directory
- CSV output saved to configuration directory as `ha_integrations.csv`
- Integration list includes name, version, and custom/core status
- Configurable daily update time (24-hour format)
- Manual export service (`integration_list_exporter.export_integrations`)
- HACS integration support

[1.1.1]: https://github.com/YOUR_USERNAME/integration-list-exporter/releases/tag/v1.1.1
[1.1.0]: https://github.com/YOUR_USERNAME/integration-list-exporter/releases/tag/v1.1.0
[1.0.0]: https://github.com/YOUR_USERNAME/integration-list-exporter/releases/tag/v1.0.0
