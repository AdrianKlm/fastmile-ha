"""Shared entity helpers for FastMile."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.const import CONF_HOST
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


def snapshot_get(snapshot: Any, key: str, default: Any = None) -> Any:
    """Read a value from a snapshot-like object."""
    if snapshot is None:
        return default

    if isinstance(snapshot, Mapping):
        return snapshot.get(key, default)

    return getattr(snapshot, key, default)


def snapshot_device_identifiers(snapshot: Any) -> set[tuple[str, str]]:
    """Build extra identifiers from snapshot data when available."""
    identifiers: set[tuple[str, str]] = set()
    for key in ("serial_number", "imei", "device_id"):
        value = snapshot_get(snapshot, key)
        if value:
            identifiers.add((DOMAIN, str(value)))
    return identifiers


class FastMileEntity(CoordinatorEntity):
    """Base class for FastMile entities."""

    _attr_has_entity_name = False

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator)
        self.entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the router entry."""
        snapshot = self.coordinator.data
        identifiers = {(DOMAIN, self.entry.data[CONF_HOST])}
        identifiers.update(snapshot_device_identifiers(snapshot))

        return DeviceInfo(
            identifiers=identifiers,
            name=snapshot_get(snapshot, "model") or self.entry.data[CONF_HOST],
            manufacturer="FastMile",
            model=snapshot_get(snapshot, "model"),
        )
