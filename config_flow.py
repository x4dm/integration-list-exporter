"""Config flow for Integration List Exporter."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_UPDATE_TIME

_LOGGER = logging.getLogger(__name__)

class IntegrationListExporterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Integration List Exporter."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate time format
            try:
                time_str = user_input.get("update_time", DEFAULT_UPDATE_TIME)
                hours, minutes = map(int, time_str.split(":"))
                if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                    errors["update_time"] = "invalid_time"
                else:
                    return self.async_create_entry(
                        title="Integration List Exporter",
                        data=user_input
                    )
            except (ValueError, AttributeError):
                errors["update_time"] = "invalid_time"

        data_schema = vol.Schema({
            vol.Optional("update_time", default=DEFAULT_UPDATE_TIME): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "update_time": "Time to run daily export (HH:MM format, 24-hour)"
            }
        )