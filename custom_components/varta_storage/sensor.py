"""Sensor platform for the unified VARTA Storage integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VartaConfigEntry
from .const import DOMAIN, SENSORS, VartaSensorEntityDescription


async def async_setup_entry(
    hass,
    entry: VartaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up VARTA sensors."""
    async_add_entities(
        VartaSensor(entry, description)
        for description in SENSORS
        if description.source != "web" or entry.runtime_data.web_coordinator is not None
    )


class VartaSensor(CoordinatorEntity, SensorEntity):
    """A VARTA sensor backed by Modbus or WebIF data."""

    _attr_has_entity_name = True

    def __init__(
        self,
        entry: VartaConfigEntry,
        description: VartaSensorEntityDescription,
    ) -> None:
        coordinator = (
            entry.runtime_data.modbus_coordinator
            if description.source == "modbus"
            else entry.runtime_data.web_coordinator
        )
        super().__init__(coordinator)
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

    @property
    def native_value(self) -> Any:
        """Return the current value."""
        if self.entity_description.source == "modbus":
            device = self.coordinator.device
            key = self.entity_description.source_key
            values = {
                "state": device.battery.state.name.lower() if device.battery.state is not None else None,
                "active_power": device.battery.active_power,
                "charging_power": device.battery.charging_power,
                "discharging_power": device.battery.discharging_power,
                "state_of_charge": device.battery.state_of_charge,
                "grid_power": device.grid.power,
                "installed_capacity": device.battery.installed_capacity,
                "error_code": device.battery.error_code,
                "external_control_timeout": device.battery.external_control_timeout,
                "installed_battery_modules": device.identity.installed_battery_modules,
                "ems_software": device.identity.ems_software,
                "ens_software": device.identity.ens_software,
                "software": device.identity.software,
                "ac_to_dc_energy": device.battery.ac_to_dc_energy,
            }
            return values.get(key)

        return self.coordinator.data.get("summary", {}).get(self.entity_description.source_key)
