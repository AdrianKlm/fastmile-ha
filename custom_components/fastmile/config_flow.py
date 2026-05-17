"""Config flow for FastMile."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
)


class FastMileConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FastMile."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
            }
        )
        return self.async_show_form(step_id="user", data_schema=data_schema)
