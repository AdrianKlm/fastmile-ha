# FastMile HA Custom Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a professional Home Assistant custom integration that talks directly to the FastMile router and reuses `fastmile-parser` for all HTML parsing.

**Architecture:** The integration lives as a Home Assistant custom component under `custom_components/fastmile`. It owns config flow, polling, entity setup, and diagnostics, but it does not duplicate router parsing: each refresh fetches the router HTML with `fastmile_parser.router_client.RouterClient` and converts it with `fastmile_parser.scraper.parse_snapshot`. A `DataUpdateCoordinator` keeps the latest snapshot in memory for all entities so HA only refreshes once per interval.

**Tech Stack:** Home Assistant custom components, Python, `fastmile-parser`, `DataUpdateCoordinator`, pytest-homeassistant-custom-component.

---

### Task 1: Bootstrap the custom component package

**Files:**
- Create: `custom_components/fastmile/__init__.py`
- Create: `custom_components/fastmile/const.py`
- Create: `custom_components/fastmile/manifest.json`
- Create: `custom_components/fastmile/strings.json`
- Create: `custom_components/fastmile/translations/en.json`
- Create: `README.md`
- Create: `pyproject.toml`
- Create: `tests/conftest.py`
- Create: `tests/test_manifest.py`

- [ ] **Step 1: Write the failing test that HA can import the integration manifest**

```python
import json
from pathlib import Path


def test_manifest_declares_fastmile_parser_dependency():
    manifest = json.loads(Path("custom_components/fastmile/manifest.json").read_text())
    assert "fastmile-parser>=0.1.0" in manifest["requirements"]
    assert manifest["iot_class"] == "local_polling"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_manifest.py -q`

Expected: fail because the package tree and manifest do not exist yet.

- [ ] **Step 3: Write the minimal component skeleton**

```python
# custom_components/fastmile/__init__.py
DOMAIN = "fastmile"


async def async_setup(hass, config):
    return True
```

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "fastmile-ha"
version = "0.1.0"
dependencies = [
  "pytest>=8.0",
  "pytest-homeassistant-custom-component>=0.13",
]
```

```python
# tests/conftest.py
pytest_plugins = ["pytest_homeassistant_custom_component"]
```

```json
{
  "domain": "fastmile",
  "name": "FastMile",
  "codeowners": ["@adrian"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/adrian/fastmile-ha",
  "iot_class": "local_polling",
  "requirements": ["fastmile-parser>=0.1.0"],
  "version": "0.1.0"
}
```

- [ ] **Step 4: Run the test again to verify it passes**

Run: `pytest tests/test_manifest.py -q`

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add custom_components pyproject.toml README.md tests
git commit -m "feat: bootstrap fastmile ha integration"
```

### Task 2: Add config flow and coordinator-based polling

**Files:**
- Create: `custom_components/fastmile/config_flow.py`
- Create: `custom_components/fastmile/coordinator.py`
- Modify: `custom_components/fastmile/__init__.py`
- Modify: `custom_components/fastmile/const.py`
- Create: `tests/test_config_flow.py`
- Create: `tests/test_coordinator.py`

- [ ] **Step 1: Write the failing config-flow test**

```python
from homeassistant.data_entry_flow import FlowResultType


async def test_config_flow_shows_form(hass):
    result = await hass.config_entries.flow.async_init(
        "fastmile", context={"source": "user"}, data={}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_config_flow.py -q`

Expected: import or integration-missing failure.

- [ ] **Step 3: Implement a config flow that collects router host and credentials**

```python
class FastMileConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_HOST], data=user_input)
        return self.async_show_form(step_id="user", data_schema=data_schema)
```

```python
data_schema = vol.Schema(
    {
        vol.Required(CONF_HOST, default="192.168.0.1"): str,
        vol.Required(CONF_USERNAME, default="admin"): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_TIMEOUT, default=30): int,
        vol.Optional(CONF_SCAN_INTERVAL, default=15): int,
    }
)
```

```python
class FastMileDataUpdateCoordinator(DataUpdateCoordinator):
    async def _async_update_data(self):
        return await self.hass.async_add_executor_job(self._load_snapshot)
```

- [ ] **Step 4: Run the config-flow and coordinator tests again**

Run: `pytest tests/test_config_flow.py tests/test_coordinator.py -q`

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add custom_components/fastmile/config_flow.py custom_components/fastmile/coordinator.py custom_components/fastmile/__init__.py custom_components/fastmile/const.py tests/test_config_flow.py tests/test_coordinator.py
git commit -m "feat: add fastmile config flow and polling"
```

### Task 3: Add sensor and binary sensor entities

**Files:**
- Create: `custom_components/fastmile/sensor.py`
- Create: `custom_components/fastmile/binary_sensor.py`
- Create: `custom_components/fastmile/entity.py`
- Modify: `custom_components/fastmile/__init__.py`
- Create: `tests/test_sensor.py`

- [ ] **Step 1: Write the failing entity test**

```python
from tests.common import MockConfigEntry


async def test_sensor_reports_rsrp_and_device_info(hass):
    entry = MockConfigEntry(
        domain="fastmile",
        data={
            "host": "192.168.0.1",
            "username": "admin",
            "password": "secret",
            "timeout": 30,
            "scan_interval": 15,
        },
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.fastmile_signal_rsrp")

    assert state.state == "-106"
    assert state.attributes["unit_of_measurement"] == "dBm"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_sensor.py -q`

Expected: entity/platform not found.

- [ ] **Step 3: Implement a small entity base and the first sensor set**

```python
class FastMileSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True

    @property
    def native_value(self):
        return self._value_from_snapshot()
```

```python
SENSOR_TYPES = [
    ("signal_rsrp", "RSRP", "dBm"),
    ("signal_rsrq", "RSRQ", "dB"),
    ("signal_rssi", "RSSI", "dBm"),
    ("signal_sinr", "SINR", "dB"),
    ("traffic_lte_download_gb", "LTE download", "GB"),
    ("traffic_lte_upload_gb", "LTE upload", "GB"),
]
```

```python
class FastMileOnlineBinarySensor(CoordinatorEntity, BinarySensorEntity):
    @property
    def is_on(self):
        return self.coordinator.data.online
```

- [ ] **Step 4: Run the entity tests again**

Run: `pytest tests/test_sensor.py -q`

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add custom_components/fastmile/sensor.py custom_components/fastmile/binary_sensor.py custom_components/fastmile/entity.py tests/test_sensor.py
git commit -m "feat: add fastmile sensors"
```

### Task 4: Add diagnostics and polish the HA package

**Files:**
- Create: `custom_components/fastmile/diagnostics.py`
- Modify: `custom_components/fastmile/manifest.json`
- Modify: `README.md`
- Create: `tests/test_diagnostics.py`

- [ ] **Step 1: Write the failing diagnostics test**

```python
from tests.common import MockConfigEntry


async def test_diagnostics_redacts_credentials(hass):
    entry = MockConfigEntry(
        domain="fastmile",
        data={
            "host": "192.168.0.1",
            "username": "admin",
            "password": "secret",
            "timeout": 30,
            "scan_interval": 15,
        },
    )
    entry.add_to_hass(hass)
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["entry_data"]["password"] == "REDACTED"
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `pytest tests/test_diagnostics.py -q`

Expected: diagnostics module missing.

- [ ] **Step 3: Implement diagnostics with redaction and a clean README setup path**

```python
async def async_get_config_entry_diagnostics(hass, entry):
    return {
        "entry_data": {
            **entry.data,
            "password": "REDACTED",
        },
        "snapshot": asdict(coordinator.data),
    }
```

```markdown
## Installation

Copy `custom_components/fastmile` into your Home Assistant `custom_components` directory, restart HA, then add FastMile from Settings -> Devices & services.
```

- [ ] **Step 4: Run the diagnostics test again plus the full HA test suite**

Run: `pytest tests/test_diagnostics.py tests/test_config_flow.py tests/test_coordinator.py tests/test_sensor.py -q`

Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add custom_components/fastmile/diagnostics.py custom_components/fastmile/manifest.json README.md tests/test_diagnostics.py
git commit -m "feat: add fastmile diagnostics and docs"
```
