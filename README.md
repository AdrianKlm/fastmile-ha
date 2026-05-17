# FastMile HA

Home Assistant custom integration for FastMile routers.

The config flow collects router host, request timeout, and polling interval. The polling interval is in seconds.

## Installation

1. Copy `custom_components/fastmile` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. In Home Assistant, go to `Settings` > `Devices & services` > `Add integration` and select `FastMile`.

## Setup

Enter the router host, timeout, and polling interval when prompted. After setup, Home Assistant creates the FastMile entities and keeps them updated using local polling.
