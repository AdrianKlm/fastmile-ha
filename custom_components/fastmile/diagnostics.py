"""Diagnostics support for FastMile."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

REDACT_KEYS = {
    "access_token",
    "auth_token",
    "cookie",
    "cookies",
    "password",
    "secret",
    "token",
    "username",
}


def _redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: "REDACTED" if key in REDACT_KEYS else _redact(inner)
            for key, inner in value.items()
        }

    if isinstance(value, list):
        return [_redact(item) for item in value]

    if isinstance(value, tuple):
        return tuple(_redact(item) for item in value)

    return value


def _snapshot_data(snapshot: Any) -> Any:
    if snapshot is None:
        return None

    if isinstance(snapshot, Mapping):
        return snapshot

    if hasattr(snapshot, "__dict__"):
        return vars(snapshot)

    return snapshot


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a FastMile config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "entry_data": _redact({"data": entry.data, "options": entry.options}),
        "snapshot": _redact(_snapshot_data(coordinator.data)),
    }
