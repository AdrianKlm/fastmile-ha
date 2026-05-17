"""Sensor platform for FastMile."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import DOMAIN
from .entity import FastMileEntity, snapshot_path


SENSOR_TYPES: tuple[tuple[str, SensorEntityDescription, tuple[object, ...]], ...] = (
    ("signal_rsrp", SensorEntityDescription(key="signal_rsrp", name="RSRP", native_unit_of_measurement="dBm"), ("lte", "active", 0, "rsrp")),
    ("signal_rsrq", SensorEntityDescription(key="signal_rsrq", name="RSRQ", native_unit_of_measurement="dB"), ("lte", "active", 0, "rsrq")),
    ("signal_rssi", SensorEntityDescription(key="signal_rssi", name="RSSI", native_unit_of_measurement="dBm"), ("lte", "active", 0, "rssi")),
    ("signal_sinr", SensorEntityDescription(key="signal_sinr", name="SINR", native_unit_of_measurement="dB"), ("lte", "active", 0, "sinr")),
    ("download", SensorEntityDescription(key="download", name="Download", native_unit_of_measurement="GB"), ("data", "eth", "download", "val_gb")),
    ("upload", SensorEntityDescription(key="upload", name="Upload", native_unit_of_measurement="GB"), ("data", "eth", "upload", "val_gb")),
)


class FastMileSensor(FastMileEntity, SensorEntity):
    """Representation of a FastMile sensor."""

    _attr_has_entity_name = True
    entity_description: SensorEntityDescription

    def __init__(self, coordinator, entry, description: SensorEntityDescription, value_path: tuple[object, ...]) -> None:
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._value_path = value_path
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement

    @property
    def native_value(self):
        """Return the latest value from the coordinator snapshot."""
        return snapshot_path(self.coordinator.data, *self._value_path)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up FastMile sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(FastMileSensor(coordinator, entry, description, value_path) for _, description, value_path in SENSOR_TYPES)
