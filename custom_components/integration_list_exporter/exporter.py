"""Integration exporter functionality."""
import csv
import io
import logging
import os
from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_custom_components, async_get_integration
from homeassistant.helpers.hassio import is_hassio
from homeassistant.util import dt as dt_util

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
            
            # Gather add-on information
            addons = await self._get_addons()
            
            # Gather integration information
            integrations = await self._get_integrations()
            
            # Build CSV content in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write system information section
            writer.writerow(["System Information"])
            writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            
            for key, value in system_info.items():
                writer.writerow([key, value])
            
            # Empty row separator
            writer.writerow([])
            
            # Write add-ons section
            writer.writerow(["Add-on Name", "Version"])
            if addons:
                for addon in sorted(addons, key=lambda x: x['name'].lower()):
                    writer.writerow([addon['name'], addon['version']])
            else:
                writer.writerow(["No add-ons installed or supervisor not available", ""])
            
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
            
            # Write to file asynchronously
            csv_content = output.getvalue()
            await self.hass.async_add_executor_job(
                self._write_file, csv_path, csv_content
            )
            
            _LOGGER.info(f"Successfully generated {CSV_FILENAME} with {len(integrations)} integrations and {len(addons)} add-ons")
            
        except Exception as e:
            _LOGGER.error(f"Error generating CSV: {e}", exc_info=True)
    
    def _write_file(self, path: str, content: str) -> None:
        """Write content to file (runs in executor)."""
        with open(path, 'w', newline='', encoding='utf-8') as f:
            f.write(content)

    async def _get_system_info(self) -> dict:
        """Get system information."""
        info = {}
        
        try:
            # Home Assistant version
            info["Home Assistant Version"] = self.hass.config.as_dict().get("version", "Unknown")
            
            # Python version
            import sys
            info["Python Version"] = sys.version.split()[0]
            
            # Config directory
            info["Config Directory"] = self.hass.config.config_dir
            
            # Check if running under supervisor
            is_supervised = is_hassio(self.hass)
            info["Supervisor"] = str(is_supervised)
            
            # Try to get supervisor/host information
            if is_supervised:
                try:
                    hassio = self.hass.data.get("hassio")
                    
                    if hassio:
                        # Get host info
                        host_info = await hassio.get_host_info()
                        if host_info:
                            info["Operating System Family"] = host_info.get("operating_system", "Unknown")
                            info["Operating System Version"] = host_info.get("os_version", "Unknown")
                            info["CPU Architecture"] = host_info.get("chassis", "Unknown")
                            info["Host Operating System"] = host_info.get("deployment", "Unknown")
                            info["Board"] = host_info.get("board", "Unknown")
                            
                            # Disk information
                            disk_total = host_info.get("disk_total")
                            disk_used = host_info.get("disk_used")
                            disk_free = host_info.get("disk_free")
                            
                            if disk_total:
                                info["Disk Total"] = f"{disk_total} GB"
                            if disk_used:
                                info["Disk Used"] = f"{disk_used} GB"
                            
                            # Determine disk health (simple check)
                            if disk_total and disk_free:
                                free_percentage = (disk_free / disk_total) * 100
                                info["Disk Healthy"] = str(free_percentage > 10)  # More than 10% free is "healthy"
                            
                        # Get supervisor info
                        supervisor_info = await hassio.get_supervisor_info()
                        if supervisor_info:
                            info["Supervisor Update Channel"] = supervisor_info.get("channel", "Unknown")
                            info["Supervisor Version"] = supervisor_info.get("version", "Unknown")
                        
                        # Get core info for additional details
                        core_info = await hassio.get_core_info()
                        if core_info:
                            info["Docker"] = str(True)  # If supervisor exists, Docker is being used
                        
                        # Get OS info
                        os_info = await hassio.get_os_info()
                        if os_info:
                            info["Agent Version"] = os_info.get("agent_version", "Unknown")
                        
                        # Get Docker version from host info
                        if host_info:
                            info["Docker Version"] = host_info.get("docker_version", "Unknown")
                        
                except Exception as e:
                    _LOGGER.debug(f"Error getting supervisor info: {e}")
                    # Set defaults if we can't get supervisor info
                    info["Docker"] = "Unknown"
                    info["Operating System Family"] = "Unknown"
                    info["Operating System Version"] = "Unknown"
                    info["CPU Architecture"] = "Unknown"
                    info["Host Operating System"] = "Unknown"
                    info["Supervisor Update Channel"] = "Unknown"
                    info["Supervisor Version"] = "Unknown"
                    info["Agent Version"] = "Unknown"
                    info["Docker Version"] = "Unknown"
                    info["Disk Total"] = "Unknown"
                    info["Disk Used"] = "Unknown"
                    info["Disk Healthy"] = "Unknown"
                    info["Board"] = "Unknown"
            else:
                # Not supervised - set appropriate values
                info["Docker"] = "False"
                info["Operating System Family"] = "Unknown"
                info["Operating System Version"] = "Unknown"
                info["CPU Architecture"] = "Unknown"
                info["Host Operating System"] = "N/A (Container/Core)"
                info["Supervisor Update Channel"] = "N/A"
                info["Supervisor Version"] = "N/A"
                info["Agent Version"] = "N/A"
                info["Docker Version"] = "Unknown"
                info["Disk Total"] = "Unknown"
                info["Disk Used"] = "Unknown"
                info["Disk Healthy"] = "Unknown"
                info["Board"] = "N/A"
            
            # Check if running as root
            try:
                import os as os_module
                info["User Root"] = str(os_module.geteuid() == 0)
            except Exception:
                info["User Root"] = "Unknown"
            
            # Check for virtual environment
            info["Virtual Environment"] = str(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))
            
        except Exception as e:
            _LOGGER.warning(f"Error gathering system info: {e}")
        
        return info

    async def _get_addons(self) -> list[dict]:
        """Get list of all installed add-ons."""
        addons = []
        
        try:
            if not is_hassio(self.hass):
                return addons
            
            hassio = self.hass.data.get("hassio")
            if not hassio:
                return addons
            
            # Get add-ons info
            addons_info = await hassio.get_addons_info()
            if addons_info and "addons" in addons_info:
                for addon in addons_info["addons"]:
                    addons.append({
                        'name': addon.get('name', 'Unknown'),
                        'version': addon.get('version', 'Unknown')
                    })
                    
        except Exception as e:
            _LOGGER.debug(f"Error gathering add-ons: {e}")
        
        return addons

    async def _get_integrations(self) -> list[dict]:
        """Get list of all integrations with versions."""
        integrations = []
        
        try:
            # Get custom components
            custom_components = await async_get_custom_components(self.hass)
            custom_domains = set(custom_components.keys())
            
            # Track which domains we've already added
            added_domains = set()
            
            # Get all loaded integrations from config entries
            for entry in self.hass.config_entries.async_entries():
                domain = entry.domain
                
                if domain in added_domains:
                    continue
                
                try:
                    integration = await async_get_integration(self.hass, domain)
                    
                    # Determine if custom
                    is_custom = domain in custom_domains
                    
                    # Get version - try multiple methods
                    version = "N/A"
                    
                    # Method 1: Direct version attribute
                    if hasattr(integration, 'version') and integration.version:
                        version = integration.version
                    
                    # Method 2: From manifest
                    elif hasattr(integration, 'manifest') and integration.manifest:
                        manifest_version = integration.manifest.get('version')
                        if manifest_version:
                            version = manifest_version
                    
                    # Method 3: For core integrations, use HA version
                    if version == "N/A" and not is_custom:
                        version = self.hass.config.as_dict().get("version", "N/A")
                    
                    integrations.append({
                        'name': integration.name,
                        'domain': domain,
                        'version': version,
                        'custom': 'Yes' if is_custom else 'No'
                    })
                    
                    added_domains.add(domain)
                        
                except Exception as e:
                    _LOGGER.debug(f"Could not load integration {domain}: {e}")
            
            # Also add integrations that may not have config entries but are loaded
            for domain in self.hass.config.components:
                if domain in added_domains:
                    continue
                    
                try:
                    integration = await async_get_integration(self.hass, domain)
                    
                    is_custom = domain in custom_domains
                    
                    # Get version
                    version = "N/A"
                    
                    if hasattr(integration, 'version') and integration.version:
                        version = integration.version
                    elif hasattr(integration, 'manifest') and integration.manifest:
                        manifest_version = integration.manifest.get('version')
                        if manifest_version:
                            version = manifest_version
                    
                    # For core integrations without explicit version, use HA version
                    if version == "N/A" and not is_custom:
                        version = self.hass.config.as_dict().get("version", "N/A")
                    
                    integrations.append({
                        'name': integration.name,
                        'domain': domain,
                        'version': version,
                        'custom': 'Yes' if is_custom else 'No'
                    })
                    
                    added_domains.add(domain)
                        
                except Exception as e:
                    _LOGGER.debug(f"Could not load component {domain}: {e}")
                    
        except Exception as e:
            _LOGGER.error(f"Error gathering integrations: {e}", exc_info=True)
        
        return integrations
