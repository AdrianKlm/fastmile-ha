"""Tests for the FastMile config flow."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType

from custom_components.fastmile.const import (
    CONF_HOST,
    CONF_SCAN_INTERVAL,
    CONF_TIMEOUT,
    DOMAIN,
)


async def test_config_flow_shows_form(hass, enable_custom_integrations):
    """The user flow should present a form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_config_flow_creates_entry_with_collected_values(
    hass, enable_custom_integrations, monkeypatch
):
    """The user flow should store the submitted connection settings."""
    async def fake_setup_entry(*args, **kwargs):
        return True

    monkeypatch.setattr("custom_components.fastmile.async_setup_entry", fake_setup_entry)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )

    user_input = {
        CONF_HOST: "192.168.0.1",
        CONF_TIMEOUT: 20,
        CONF_SCAN_INTERVAL: 15,
    }

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input=user_input,
    )

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == user_input[CONF_HOST]
    assert result["data"] == user_input
