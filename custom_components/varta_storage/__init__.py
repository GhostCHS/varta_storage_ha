"""The VARTA Storage integration."""

from __future__ import annotations

from dataclasses import fields, is_dataclass
from datetime import timedelta
from typing import Any

import async_timeout
from vartastorage import vartastorage

from homeassistant import config_entries, core
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, LOGGER

PLATFORMS: list[Platform] = [Platform.SENSOR]


def flatten_dataclass(obj: Any) -> dict[str, Any]:
    """Flatten nested dataclasses into a plain dict."""
    if not is_dataclass(obj):
        return {}

    flat_dict: dict[str, Any] = {}
    for field in fields(obj):
        value = getattr(obj, field.name)
        if is_dataclass(value):
            flat_dict.update(flatten_dataclass(value))
        else:
            flat_dict[field.name] = value
    return flat_dict


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up VARTA Storage from a config entry."""
    required_fields = [
        "scan_interval_modbus",
        "scan_interval_cgi",
        "host",
        "host_cgi",
        "port",
        "username",
        "password",
    ]
    missing_fields = [field for field in required_fields if field not in entry.data]
    if missing_fields:
        message = (
            "The new version of VARTA Storage integration requires reconfiguration "
            "due to newly introduced configuration options. "
            "Please reconfigure the integration in Home Assistant."
        )
        LOGGER.error(message)
        hass.async_create_task(
            hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "VARTA Storage Integration Requires Reconfiguration",
                    "message": message,
                    "notification_id": "varta_storage_reconfigure",
                },
                blocking=False,
            )
        )
        raise ConfigEntryNotReady(
            f"Missing required fields: {', '.join(missing_fields)}"
        )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    scan_interval_modbus = timedelta(seconds=entry.data["scan_interval_modbus"])
    scan_interval_cgi = timedelta(seconds=entry.data["scan_interval_cgi"])

    async def async_update_modbus():
        """Fetch modbus data in executor."""

        def sync_update():
            try:
                varta = vartastorage.VartaStorage(
                    entry.data["host"],
                    entry.data["port"],
                    False,
                    entry.data["username"],
                    entry.data["password"],
                )
                result = varta.get_all_data_modbus()
                return flatten_dataclass(result)
            except Exception as err:
                LOGGER.info("Cannot retrieve Modbus data from VARTA device: %s", err)
                raise UpdateFailed(
                    "Cannot retrieve Modbus data from the VARTA device."
                ) from err

        try:
            async with async_timeout.timeout(10):
                return await hass.async_add_executor_job(sync_update)
        except Exception as err:
            raise UpdateFailed("Error communicating with Modbus API") from err

    async def async_update_cgi():
        """Fetch CGI data in executor."""

        def sync_update():
            try:
                host = entry.data["host_cgi"] or entry.data["host"]

                varta = vartastorage.VartaStorage(
                    host,
                    entry.data["port"],
                    True,
                    entry.data["username"],
                    entry.data["password"],
                )

                ems_data = varta.get_ems_cgi()
                energy_data = varta.get_energy_cgi()
                info_data = varta.get_info_cgi()
                service_data = varta.get_service_cgi()

                if (
                    hasattr(energy_data, "total_charge_cycles")
                    and isinstance(energy_data.total_charge_cycles, list)
                    and len(energy_data.total_charge_cycles) == 1
                ):
                    energy_data.total_charge_cycles = energy_data.total_charge_cycles[0]

                merged: dict[str, Any] = {}
                merged.update(flatten_dataclass(ems_data))
                merged.update(flatten_dataclass(energy_data))
                merged.update(flatten_dataclass(info_data))
                merged.update(flatten_dataclass(service_data))
                return merged

            except Exception as err:
                LOGGER.info("Cannot retrieve CGI data from VARTA device: %s", err)
                raise UpdateFailed(
                    "Cannot retrieve CGI data from the VARTA device."
                ) from err

        try:
            async with async_timeout.timeout(10):
                return await hass.async_add_executor_job(sync_update)
        except Exception as err:
            raise UpdateFailed("Error communicating with CGI API") from err

    coordinators: dict[str, DataUpdateCoordinator] = {}

    modbus_coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name="modbus_sensor",
        update_method=async_update_modbus,
        update_interval=scan_interval_modbus,
        always_update=False,
    )
    await modbus_coordinator.async_config_entry_first_refresh()
    coordinators["modbus"] = modbus_coordinator

    if entry.data.get("cgi"):
        cgi_coordinator = DataUpdateCoordinator(
            hass,
            LOGGER,
            name="cgi_sensor",
            update_method=async_update_cgi,
            update_interval=scan_interval_cgi,
            always_update=False,
        )
        await cgi_coordinator.async_config_entry_first_refresh()
        coordinators["cgi"] = cgi_coordinator

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_reload_entry(
    hass: core.HomeAssistant, config_entry: config_entries.ConfigEntry
):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(
    hass: core.HomeAssistant, entry: config_entries.ConfigEntry
) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
