# FastMile HA

Home Assistant custom integration for FastMile routers.

The config flow collects router host, request timeout, and polling interval. The polling interval is in seconds.

## Install with HACS

1. In Home Assistant, open `HACS`.
2. Add `AdrianKlm/fastmile-ha` as a custom repository of type `Integration`.
3. Install `FastMile HA` from HACS.
4. Restart Home Assistant.
5. In Home Assistant, go to `Settings` > `Devices & services` > `Add integration` and select `FastMile`.

## Setup

Enter the router host, timeout, and polling interval when prompted. After setup, Home Assistant creates the FastMile entities and keeps them updated using local polling.

## Reconfigure

Open the integration in `Settings` > `Devices & services`, choose `FastMile`, then use `Reconfigure` to change the host, timeout, or polling interval.
