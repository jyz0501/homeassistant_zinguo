"""Config flow for Zinguo integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    CONF_ACCOUNT,
    CONF_PASSWORD,
    CONF_MAC,
    CONF_NAME,
    DOMAIN
)

_LOGGER = logging.getLogger(__name__)

class ZinguoConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zinguo."""
    
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL
    
    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            # Validate the input
            if not user_input[CONF_ACCOUNT].startswith("1") and len(user_input[CONF_ACCOUNT]) == 11:
                errors[CONF_ACCOUNT] = "invalid_account"
            elif len(user_input[CONF_PASSWORD]) < 6:
                errors[CONF_PASSWORD] = "invalid_password"
            elif len(user_input[CONF_MAC]) != 12:
                errors[CONF_MAC] = "invalid_mac"
            else:
                # Check if we have an existing entry
                await self.async_set_unique_id(user_input[CONF_MAC])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, "Zinguo Bathroom Fan"),
                    data=user_input
                )
        
        # Show the form
        data_schema = vol.Schema({
            vol.Required(CONF_ACCOUNT): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_MAC): str,
            vol.Optional(CONF_NAME, default="Zinguo Bathroom Fan"): str,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return ZinguoOptionsFlowHandler(config_entry)

class ZinguoOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Zinguo options."""
    
    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry
    
    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_NAME,
                    default=self.config_entry.options.get(CONF_NAME, self.config_entry.data.get(CONF_NAME, "Zinguo Bathroom Fan"))
                ): str,
            })
        )