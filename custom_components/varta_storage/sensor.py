"""Sensor platform for the unified VARTA Storage integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VartaConfigEntry
from .const import DOMAIN, SENSORS, VartaSensorEntityDescription


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VartaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up VARTA sensors."""
    async_add_entities(
        VartaSensor(entry, description)
        for description in SENSORS
        if description.source != "web" or entry.runtime_data.web_coordinator is not None
    )


class VartaSensor(SensorEntity):
    """A VARTA sensor backed by Modbus or WebIF data."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: VartaConfigEntry,
        description: VartaSensorEntityDescription,
    ) -> None:
        self.entity_description = description
        device = entry.runtime_data.device
        serial = device.identity.serial_number or entry.entry_id
        self._attr_unique_id = f"{serial}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer="VARTA",
            name="VARTA Storage",
            serial_number=device.identity.serial_number,
            sw_version=device.identity.software,
            configuration_url=f"http://{entry.data['host']}",
        )

        if description.source == "modbus":
            self._coordinator = entry.runtime_data.modbus_coordinator
        else:
            self._coordinator = entry.runtime_data.web_coordinator

    @property
    def native_value(self) -> Any:
        """Return the current value."""
        if self.entity_description.source == "modbus":
            device = self._coordinator.device
            key = self.entity_description.source_key
            if key == "state":
                return device.battery.state.name.lower() if device.battery.state is not None else None
            if key == "active_power":
                return device.battery.active_power
            if key == "charging_power":
                return device.battery.charging_power
            if key == "discharging_power":
                return device.battery.discharging_power
            if key == "state_of_charge":
                return device.battery.state_of_charge
            if key == "grid_power":
                return device.grid.power
            if key == "installed_capacity":
                return device.battery.installed_capacity
            if key == "error_code":
                return device.battery.error_code
            if key == "external_control_timeout":
                return device.battery.external_control_timeout
            if key == "installed_battery_modules":
                return device.identity.installed_battery_modules
            if key == "ems_software":
                return device.identity.ems_software
            if key == "ens_software":
                return device.identity.ens_software
            if key == "software":
                return device.identity.software
            if key == "ac_to_dc_energy":
                return device.battery.ac_to_dc_energy
            return None

        if self._coordinator is None or not self._coordinator.data:
            return None
        return self._coordinator.data.get("summary", {}).get(
            self.entity_description.source_key
        )

    @property
    def available(self) -> bool:
        """Return whether the backing coordinator is available."""
        return bool(self._coordinator and self._coordinator.last_update_success)

    async def async_update(self) -> None:
        """Update through the coordinator."""
        if self._coordinator is not None:
            await self._coordinator.async_request_refresh()
