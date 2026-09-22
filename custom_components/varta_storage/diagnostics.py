"""Diagnostics for VARTA Storage."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import issue_registry as ir

from . import VartaConfigEntry
from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: VartaConfigEntry,
) -> dict[str, Any]:
    """Return non-sensitive diagnostic information for a VARTA device."""
    runtime = entry.runtime_data
    device = runtime.device

    data: dict[str, Any] = {
        "modbus": {
            "host": entry.data.get("host"),
            "port": entry.data.get("port"),
            "unit_id": entry.data.get("unit_id"),
            "state": device.battery.state.name if device.battery.state else None,
            "active_power": device.battery.active_power,
            "charging_power": device.battery.charging_power,
            "discharging_power": device.battery.discharging_power,
            "soc": device.battery.state_of_charge,
            "grid_power": device.grid.power,
            "installed_capacity": device.battery.installed_capacity,
            "error_code": device.battery.error_code,
        }
    }

    if runtime.web_coordinator is not None:
        summary = runtime.web_coordinator.data.get("summary", {})
        data["webif"] = summary

    return data
