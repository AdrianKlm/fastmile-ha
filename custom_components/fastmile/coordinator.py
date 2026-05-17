"""Data update coordinator for FastMile."""

from __future__ import annotations

import logging
from datetime import timedelta

from fastmile_parser.router_client import RouterClient
from fastmile_parser.scraper import parse_snapshot
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_TIMEOUT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class FastMileDataUpdateCoordinator(DataUpdateCoordinator):
    """Fetch and parse the router snapshot."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.client = RouterClient(entry.data[CONF_HOST], timeout=entry.data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {entry.data[CONF_HOST]}",
            update_interval=timedelta(seconds=entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)),
        )

    async def _async_update_data(self):
        """Fetch and parse the latest snapshot."""
        try:
            html = await self.hass.async_add_executor_job(self.client.fetch_status_html)
            return await self.hass.async_add_executor_job(parse_snapshot, html)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with FastMile router: {err}") from err
