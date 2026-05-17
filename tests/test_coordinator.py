"""Tests for the FastMile data update coordinator."""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.plugins import MockConfigEntry

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


async def test_coordinator_fetches_and_parses_snapshot(
    hass, enable_custom_integrations, monkeypatch, config_entry
):
    """The coordinator should fetch HTML and parse it into a snapshot."""
    snapshot = SimpleNamespace(token="snapshot")

    class FakeRouterClient:
        def __init__(self, host: str, timeout: int) -> None:
            assert host == config_entry.data[CONF_HOST]
            assert timeout == config_entry.data[CONF_TIMEOUT]

        def fetch_status_html(self) -> str:
            return "<html><body>router</body></html>"

    def fake_parse_snapshot(html: str):
        assert html == "<html><body>router</body></html>"
        return snapshot

    monkeypatch.setattr(
        "custom_components.fastmile.coordinator.RouterClient",
        FakeRouterClient,
    )
    monkeypatch.setattr(
        "custom_components.fastmile.coordinator.parse_snapshot",
        fake_parse_snapshot,
    )

    config_entry.add_to_hass(hass)

    from custom_components.fastmile.coordinator import FastMileDataUpdateCoordinator

    coordinator = FastMileDataUpdateCoordinator(hass, config_entry)

    assert coordinator.update_interval == timedelta(seconds=5)

    result = await coordinator._async_update_data()

    assert result is snapshot


async def test_coordinator_wraps_fetch_errors(
    hass, enable_custom_integrations, monkeypatch, config_entry
):
    """The coordinator should surface fetch failures as update errors."""

    class FakeRouterClient:
        def __init__(self, host: str, timeout: int) -> None:
            pass

        def fetch_status_html(self) -> str:
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "custom_components.fastmile.coordinator.RouterClient",
        FakeRouterClient,
    )

    config_entry.add_to_hass(hass)

    from custom_components.fastmile.coordinator import FastMileDataUpdateCoordinator

    coordinator = FastMileDataUpdateCoordinator(hass, config_entry)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()
