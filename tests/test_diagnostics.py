"""Tests for FastMile diagnostics."""

from __future__ import annotations

from types import SimpleNamespace

from pytest_homeassistant_custom_component.plugins import MockConfigEntry

from custom_components.fastmile.const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    DOMAIN,
)


async def test_diagnostics_redacts_credentials_and_summarizes_snapshot(hass):
    """Diagnostics should keep secrets out of the response."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_HOST: "192.168.0.1",
            CONF_TIMEOUT: 12,
            CONF_SCAN_INTERVAL: 5,
        },
        options={"nested": {"token": "nested-secret"}},
    )
    entry.add_to_hass(hass)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = SimpleNamespace(
        data=SimpleNamespace(
            online=True,
            model="FastMile 5G",
            serial_number="SN123",
            imei="IMEI456",
            device_id="device-789",
            rsrp=-91,
            rsrq=-12,
            rssi=-71,
            sinr=18,
            lte_download_gb=42.5,
            lte_upload_gb=7.25,
            token="snapshot-token",
        )
    )

    from custom_components.fastmile.diagnostics import async_get_config_entry_diagnostics

    diagnostics = await async_get_config_entry_diagnostics(hass, entry)

    assert diagnostics["entry_data"]["options"]["nested"]["token"] == "REDACTED"

    assert diagnostics["snapshot"] == {
        "online": True,
        "model": "FastMile 5G",
        "serial_number": "SN123",
        "imei": "IMEI456",
        "device_id": "device-789",
        "rsrp": -91,
        "rsrq": -12,
        "rssi": -71,
        "sinr": 18,
        "lte_download_gb": 42.5,
        "lte_upload_gb": 7.25,
        "token": "REDACTED",
    }
