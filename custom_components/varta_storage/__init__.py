"""The unified VARTA Storage integration."""

from __future__ import annotations

from dataclasses import dataclass

from modbus_connection import ModbusTcpParams

from homeassistant.components.modbus import async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_UNIT_ID,
    DEFAULT_SCAN_INTERVAL_CGI,
    DEFAULT_SCAN_INTERVAL_MODBUS,
    DOMAIN,
)
from .coordinator import (
    VartaModbusCoordinator,
    VartaWebCoordinator,
    create_web_coordinator,
)
from .vendor.varta_modbus import VartaStorage

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.NUMBER]


@dataclass
class VartaRuntimeData:
    """Runtime data for one VARTA config entry."""

    device: VartaStorage
    modbus_coordinator: VartaModbusCoordinator
    web_coordinator: VartaWebCoordinator | None


VartaConfigEntry = ConfigEntry[VartaRuntimeData]


async def async_setup_entry(hass: HomeAssistant, entry: VartaConfigEntry) -> bool:
    """Set up VARTA Storage from a config entry."""
    params = ModbusTcpParams(
        host=entry.data[CONF_HOST],
        port=entry.data.get(CONF_PORT, 502),
    )

    unit = async_get_unit(
        hass,
        entry,
        params,
        entry.data.get(CONF_UNIT_ID, 1),
    )

    device = VartaStorage(unit)
    modbus_coordinator = VartaModbusCoordinator(
        hass,
        device,
        entry.data.get("scan_interval_modbus", DEFAULT_SCAN_INTERVAL_MODBUS),
    )

    try:
        await modbus_coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(
            "Unable to communicate with VARTA via Modbus"
        ) from err

    web_coordinator = None
    if entry.data.get("cgi", True):
        web_host = entry.data.get("host_cgi") or entry.data[CONF_HOST]
        candidate = create_web_coordinator(
            hass,
            web_host,
            entry.data.get("username", "user1"),
            entry.data.get("password", ""),
            entry.data.get("scan_interval_cgi", DEFAULT_SCAN_INTERVAL_CGI),
        )
        try:
            await candidate.async_config_entry_first_refresh()
        except Exception:
            # CGI is optional. Modbus remains available when the WebIF is
            # disabled, unavailable, or not supported by the device.
            web_coordinator = None
        else:
            web_coordinator = candidate

    entry.runtime_data = VartaRuntimeData(
        device=device,
        modbus_coordinator=modbus_coordinator,
        web_coordinator=web_coordinator,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: VartaConfigEntry) -> bool:
    """Unload a VARTA config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await entry.runtime_data.device.external_control.async_stop()
    return unload_ok
