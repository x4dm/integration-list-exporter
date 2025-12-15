# Integration List Exporter

A Home Assistant custom integration that exports all your installed integrations (core and custom) to a CSV file, along with system information.

## Features

- 📋 Exports all integrations (core + custom) to CSV
- 🖥️ Includes system information at the top of the CSV
- ⏰ Automatic daily export at a time you choose
- 🔧 Manual export via service call
- 📁 Saves to your Home Assistant configuration directory

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right and select "Custom repositories"
4. Add this repository URL and select "Integration" as the category
5. Click "Download" on the Integration List Exporter card
6. Restart Home Assistant

### Manual Installation

1. Copy the `integration_list_exporter` folder to your `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Integration List Exporter"
4. Enter your preferred daily export time (24-hour format, e.g., "03:00")
5. Click **Submit**

## Usage

### Automatic Export

The integration will automatically export your integrations list once per day at the time you configured.

### Manual Export

You can manually trigger an export at any time:

**Via Developer Tools:**
1. Go to **Developer Tools** → **Actions**
2. Select `integration_list_exporter.export_integrations`
3. Click **Perform Action**

**Via Automation:**
```yaml
action: integration_list_exporter.export_integrations
```

## Output File

The CSV file is saved as `ha_integrations.csv` in your Home Assistant configuration directory (typically `/config/`).

### File Format

```
System Information
Generated,2024-12-09 15:30:00
Home Assistant Version,2024.12.0
Installation Type,Home Assistant OS/Supervised
Python Version,3.11.5
...

Integration Name,Version,Custom Integration
Advanced SSH & Web Terminal,17.2.0,Yes
AdGuard Home,1.0.0,No
Automation,N/A,No
...
```

## Use Cases

- 📊 Feed the CSV into AI tools to analyze upgrade safety
- 📝 Documentation and backup purposes
- 🔍 Auditing your installed integrations
- 📈 Tracking integration versions over time

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Support

If you encounter any issues, please [open an issue](https://github.com/x4dm/integration-list-exporter/issues) on GitHub.

## License

MIT License
