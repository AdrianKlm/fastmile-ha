"""Tests for FastMile entities."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from homeassistant import config_entries
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.plugins import MockConfigEntry

from fastmile_parser.models import (
    ApnInfo,
    CaInfo,
    CellSignal,
    DeviceInfo,
    InterfaceData,
    LteInfo,
    Snapshot,
    SnapshotData,
    TrafficValue,
)

from custom_components.fastmile.const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    DOMAIN,
)


@pytest.fixture
def config_entry() -> MockConfigEntry:
    """Create a representative config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.0.1",
            CONF_TIMEOUT: 12,
            CONF_SCAN_INTERVAL: 5,
        },
    )


async def test_fastmile_sensors_and_binary_sensor_use_snapshot_and_device_info(
    hass, enable_custom_integrations, monkeypatch, config_entry
):
    """Entities should read snapshot data and attach to one device."""
    snapshot = Snapshot(
        device=DeviceInfo(
            model="FastMile 5G",
            software_version="1.0",
            serial_number="FM123456",
            imei="IMEI123",
            imsi="IMSI456",
            mac="AA:BB:CC:DD:EE:FF",
            lock_status="Normal",
        ),
        apns=[ApnInfo(name="internet", ipv4="10.0.0.2", ipv6=None)],
        data=SnapshotData(
            eth=InterfaceData(
                download=TrafficValue(val=1.0, unit="GB", val_gb=1.0),
                upload=TrafficValue(val=0.5, unit="GB", val_gb=0.5),
            ),
            lte=InterfaceData(
                download=TrafficValue(val=123.4, unit="GB", val_gb=123.4),
                upload=TrafficValue(val=56.7, unit="GB", val_gb=56.7),
            ),
        ),
        lte=LteInfo(
            ca=CaInfo(enb=291067, cid=13, dl_bands=[20, 3], ul_bands=[20]),
            active=[
                CellSignal(
                    pci=38,
                    earfcn=6200,
                    cell_type="CellPrimary",
                    rsrp=-87,
                    rsrq=-13,
                    rssi=-56,
                    sinr=6,
                ),
                CellSignal(
                    pci=131,
                    earfcn=1725,
                    cell_type="CellSecondary",
                    rsrp=-104,
                    rsrq=-15,
                    rssi=-69,
                    sinr=7,
                ),
            ],
            available=[],
        ),
    )

    class FakeRouterClient:
        def __init__(self, host: str, timeout: int) -> None:
            assert host == config_entry.data[CONF_HOST]
            assert timeout == config_entry.data[CONF_TIMEOUT]

        def fetch_status_html(self) -> str:
            return "<html><body>router</body></html>"

    def fake_parse_snapshot(html: str):
        assert html == "<html><body>router</body></html>"
        return snapshot

    monkeypatch.setattr("custom_components.fastmile.coordinator.RouterClient", FakeRouterClient)
    monkeypatch.setattr("custom_components.fastmile.coordinator.parse_snapshot", fake_parse_snapshot)

    config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    expected_sensors = {
        "signal_rsrp": ("-87", "dBm"),
        "signal_rsrq": ("-13", "dB"),
        "signal_rssi": ("-56", "dBm"),
        "signal_sinr": ("6", "dB"),
        "download": ("1.0", "GB"),
        "upload": ("0.5", "GB"),
    }

    device_id = None
    for unique_id, (expected_state, expected_unit) in expected_sensors.items():
        entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{config_entry.entry_id}_{unique_id}")
        assert entity_id is not None
        state = hass.states.get(entity_id)
        assert state is not None
        assert state.state == expected_state
        assert state.attributes["unit_of_measurement"] == expected_unit

        entity_entry = entity_registry.async_get(entity_id)
        assert entity_entry is not None
        if device_id is None:
            device_id = entity_entry.device_id
        assert entity_entry.device_id == device_id

    online_entity_id = entity_registry.async_get_entity_id("binary_sensor", DOMAIN, f"{config_entry.entry_id}_online")
    assert online_entity_id is not None
    online_state = hass.states.get(online_entity_id)
    assert online_state is not None
    assert online_state.state == "on"

    online_entity_entry = entity_registry.async_get(online_entity_id)
    assert online_entity_entry is not None
    assert online_entity_entry.device_id == device_id
    assert hass.states.get(online_entity_id).state == "on"

    assert device_id is not None
    device = device_registry.async_get(device_id)
    assert device is not None
    assert (DOMAIN, config_entry.data[CONF_HOST]) in device.identifiers
    assert device.name == config_entry.data[CONF_HOST]
