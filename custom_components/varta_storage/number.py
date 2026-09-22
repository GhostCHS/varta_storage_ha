"""Writable VARTA battery power limits."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.const import EntityCategory, UnitOfPower
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VartaConfigEntry
from .const import DOMAIN


class VartaNumberDescription(NumberEntityDescription):
    """Describe a writable VARTA setting."""

    field: str


NUMBERS = (
    VartaNumberDescription(
        key="maximum_discharging_power",
        name="Maximale Entladeleistung",
        field="maximum_discharging_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        native_min_value=-4000,
        native_max_value=0,
        native_step=1,
        entity_category=EntityCategory.CONFIG,
    ),
    VartaNumberDescription(
        key="maximum_charging_power",
        name="Maximale Ladeleistung",
        field="maximum_charging_power",
        native_unit_of_measurement=UnitOfPower.WATT,
        native_min_value=0,
        native_max_value=4000,
        native_step=1,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass,
    entry: VartaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up writable VARTA limits."""
    async_add_entities(
        VartaNumber(entry, description)
        for description in NUMBERS
    )


class VartaNumber(CoordinatorEntity, NumberEntity):
    """A writable VARTA power limit."""

    _attr_has_entity_name = True

    def __init__(self, entry: VartaConfigEntry, description: VartaNumberDescription) -> None:
        super().__init__(entry.runtime_data.modbus_coordinator)
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
        )

    @property
    def native_value(self) -> float | None:
        value = getattr(self.coordinator.device.battery, self.entity_description.field)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        value = int(value)
        if self.entity_description.field == "maximum_discharging_power":
            await self.coordinator.device.external_control.async_set_discharging_power(value)
        else:
            await self.coordinator.device.external_control.async_set_charging_power(value)
        await self.coordinator.async_request_refresh()
