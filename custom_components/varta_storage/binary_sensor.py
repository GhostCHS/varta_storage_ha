"""Binary sensors for the VARTA Storage integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import VartaConfigEntry
from .const import DOMAIN


DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="active_errors",
        name="Fehler aktiv",
        device_class="problem",
    ),
)


async def async_setup_entry(
    hass,
    entry: VartaConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up VARTA binary sensors."""
    if entry.runtime_data.web_coordinator is None:
        return
    async_add_entities(
        VartaErrorSensor(entry, description) for description in DESCRIPTIONS
    )


class VartaErrorSensor(CoordinatorEntity, BinarySensorEntity):
    """Report whether VARTA currently has active errors."""

    _attr_has_entity_name = True

    def __init__(self, entry: VartaConfigEntry, description) -> None:
        super().__init__(entry.runtime_data.web_coordinator)
        self.entity_description = description
        device = entry.runtime_data.device
        serial = device.identity.serial_number or entry.entry_id
        self._attr_unique_id = f"{serial}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "manufacturer": "VARTA",
            "name": "VARTA Storage",
            "serial_number": device.identity.serial_number,
            "sw_version": device.identity.software,
        }

    @property
    def is_on(self) -> bool:
        """Return true when active VARTA errors are present."""
        return bool(self.coordinator.data.get("summary", {}).get("active_errors", 0))
