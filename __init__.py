"""Integration List Exporter for Home Assistant."""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN
from .exporter import IntegrationExporter

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Integration List Exporter from a config entry."""
    
    exporter = IntegrationExporter(hass, entry)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = exporter
    
    # Generate initial CSV
    await exporter.generate_csv()
    
    # Set up daily update based on user configuration
    update_time = entry.data.get("update_time", "03:00")
    hours, minutes = map(int, update_time.split(":"))
    
    # Calculate interval until next update
    async def scheduled_update(now):
        """Run scheduled update."""
        await exporter.generate_csv()
    
    # Schedule daily updates
    async_track_time_interval(
        hass,
        scheduled_update,
        timedelta(days=1)
    )
    
    # Register service for manual updates
    async def handle_export_integrations(call: ServiceCall) -> None:
        """Handle the export integrations service call."""
        await exporter.generate_csv()
        _LOGGER.info("Manual integration export completed")
    
    hass.services.async_register(
        DOMAIN,
        "export_integrations",
        handle_export_integrations
    )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, "export_integrations")
    
    return True