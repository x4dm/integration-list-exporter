"""Integration exporter functionality."""
import csv
import logging
import os
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_custom_components, async_get_integration

from .const import CSV_FILENAME

_LOGGER = logging.getLogger(__name__)

class IntegrationExporter:
    """Handle exporting integrations to CSV."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the exporter."""
        self.hass = hass
        self.entry = entry

    async def generate_csv(self) -> None:
        """Generate the CSV file with system info and integrations."""
        try:
            config_dir = self.hass.config.config_dir
            csv_path = os.path.join(config_dir, CSV_FILENAME)
            
            # Gather system information
            system_info = await self._get_system_info()
            
            # Gather integration information
            integrations = await self._get_integrations()
            
            # Write CSV file
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write system information section
                writer.writerow(["System Information"])
                writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                
                for key, value in system_info.items():
                    writer.writerow([key, value])
                
                # Empty row separator
                writer.writerow([])
                
                # Write integration headers
                writer.writerow(["Integration Name", "Version", "Custom Integration"])
                
                # Write integration data
                for integration in sorted(integrations, key=lambda x: x['name'].lower()):
                    writer.writerow([
                        integration['name'],
                        integration['version'],
                        integration['custom']
                    ])
            
            _LOGGER.info(f"Successfully generated {CSV_FILENAME} with {len(integrations)} integrations")
            
        except Exception as e:
            _LOGGER.error(f"Error generating CSV: {e}", exc_info=True)

    async def _get_system_info(self) -> dict:
        """Get system information."""
        info = {}
        
        try:
            # Home Assistant version
            info["Home Assistant Version"] = self.hass.config.as_dict().get("version", "Unknown")
            
            # Installation type
            if hasattr(self.hass.data, 'get'):
                supervisor_data = self.hass.data.get("hassio")
                if supervisor_data:
                    info["Installation Type"] = "Home Assistant OS/Supervised"
                else:
                    info["Installation Type"] = "Home Assistant Core/Container"
            
            # Python version
            import sys
            info["Python Version"] = sys.version.split()[0]
            
            # Config directory
            info["Config Directory"] = self.hass.config.config_dir
            
            # Time zone
            info["Time Zone"] = str(self.hass.config.time_zone)
            
            # Location
            info["Latitude"] = self.hass.config.latitude
            info["Longitude"] = self.hass.config.longitude
            
        except Exception as e:
            _LOGGER.warning(f"Error gathering system info: {e}")
        
        return info

    async def _get_integrations(self) -> list[dict]:
        """Get list of all integrations."""
        integrations = []
        
        try:
            # Get custom components
            custom_components = await async_get_custom_components(self.hass)
            custom_domains = set(custom_components.keys())
            
            # Get all loaded integrations from config entries
            for entry in self.hass.config_entries.async_entries():
                domain = entry.domain
                
                try:
                    integration = await async_get_integration(self.hass, domain)
                    
                    # Determine if custom
                    is_custom = domain in custom_domains
                    
                    # Get version
                    version = getattr(integration, 'version', 'N/A')
                    if version == 'N/A' and hasattr(integration, 'manifest'):
                        version = integration.manifest.get('version', 'N/A')
                    
                    # Add to list (avoid duplicates)
                    if not any(i['name'] == integration.name for i in integrations):
                        integrations.append({
                            'name': integration.name,
                            'version': version,
                            'custom': 'Yes' if is_custom else 'No'
                        })
                        
                except Exception as e:
                    _LOGGER.debug(f"Could not load integration {domain}: {e}")
            
            # Also add integrations that may not have config entries but are loaded
            # This catches built-in integrations
            for domain in self.hass.config.components:
                try:
                    integration = await async_get_integration(self.hass, domain)
                    
                    is_custom = domain in custom_domains
                    version = getattr(integration, 'version', 'N/A')
                    if version == 'N/A' and hasattr(integration, 'manifest'):
                        version = integration.manifest.get('version', 'N/A')
                    
                    if not any(i['name'] == integration.name for i in integrations):
                        integrations.append({
                            'name': integration.name,
                            'version': version,
                            'custom': 'Yes' if is_custom else 'No'
                        })
                        
                except Exception as e:
                    _LOGGER.debug(f"Could not load component {domain}: {e}")
                    
        except Exception as e:
            _LOGGER.error(f"Error gathering integrations: {e}", exc_info=True)
        
        return integrations