"""Sensor platform for FastMile."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription

from .const import DOMAIN
from .entity import FastMileEntity, snapshot_get


def _description(key: str, name: str, native_unit_of_measurement: str, value_key: str) -> SensorEntityDescription:
    description = SensorEntityDescription(key=key, name=name, native_unit_of_measurement=native_unit_of_measurement)
    object.__setattr__(description, "value_key", value_key)
    return description


SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    _description("signal_rsrp", "RSRP", "dBm", "rsrp"),
    _description("signal_rsrq", "RSRQ", "dB", "rsrq"),
    _description("signal_rssi", "RSSI", "dBm", "rssi"),
    _description("signal_sinr", "SINR", "dB", "sinr"),
    _description("traffic_lte_download_gb", "LTE download", "GB", "lte_download_gb"),
    _description("traffic_lte_upload_gb", "LTE upload", "GB", "lte_upload_gb"),
)


class FastMileSensor(FastMileEntity, SensorEntity):
    """Representation of a FastMile sensor."""

    _attr_has_entity_name = True
    entity_description: SensorEntityDescription

    def __init__(self, coordinator, entry, description: SensorEntityDescription) -> None:
        super().__init__(coordinator, entry)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_native_unit_of_measurement = description.native_unit_of_measurement

    @property
    def native_value(self):
        """Return the latest value from the coordinator snapshot."""
        return snapshot_get(self.coordinator.data, self.entity_description.value_key)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up FastMile sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(FastMileSensor(coordinator, entry, description) for description in SENSOR_TYPES)
