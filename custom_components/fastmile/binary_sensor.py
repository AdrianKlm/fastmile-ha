"""Binary sensor platform for FastMile."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .const import DOMAIN
from .entity import FastMileEntity


ONLINE_DESCRIPTION = BinarySensorEntityDescription(key="online", name="Online")


class FastMileBinarySensor(FastMileEntity, BinarySensorEntity):
    """Representation of the FastMile router online state."""

    _attr_has_entity_name = True
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    entity_description: BinarySensorEntityDescription

    def __init__(self, coordinator, entry, description: BinarySensorEntityDescription) -> None:
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return whether the router is online."""
        return bool(self.coordinator.last_update_success)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up FastMile binary sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FastMileBinarySensor(coordinator, entry, ONLINE_DESCRIPTION)])
