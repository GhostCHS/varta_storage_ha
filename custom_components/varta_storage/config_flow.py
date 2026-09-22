"""Config flow for the unified VARTA Storage integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from modbus_connection import ModbusError, ModbusTcpParams

from homeassistant.components.modbus import async_get_temporary_unit
from homeassistant.config_entries import ConfigFlowResult, ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_UNIT_ID,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL_CGI,
    DEFAULT_SCAN_INTERVAL_MODBUS,
    DEFAULT_UNIT_ID,
    DOMAIN,
)
from .vendor.varta_modbus import VartaStorage


async def async_validate_modbus(hass, data: dict[str, Any]) -> str:
    """Validate the Modbus endpoint and return the VARTA serial number."""
    params = ModbusTcpParams(host=data[CONF_HOST].strip(), port=data[CONF_PORT])
    async with async_get_temporary_unit(hass, params, data[CONF_UNIT_ID]) as unit:
        device = VartaStorage(unit)
        await device.async_validate()
        return device.identity.serial_number or "unknown"


def _schema(data: dict[str, Any] | None = None) -> vol.Schema:
    data = data or {}
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=data.get(CONF_HOST, "")): str,
            vol.Required(CONF_PORT, default=data.get(CONF_PORT, DEFAULT_PORT)): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=65535)
            ),
            vol.Required(CONF_UNIT_ID, default=data.get(CONF_UNIT_ID, DEFAULT_UNIT_ID)): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=247)
            ),
            vol.Required(
                "scan_interval_modbus",
                default=data.get("scan_interval_modbus", DEFAULT_SCAN_INTERVAL_MODBUS),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
            vol.Required("cgi", default=data.get("cgi", True)): bool,
            vol.Optional("host_cgi", default=data.get("host_cgi", "")): str,
            vol.Optional(CONF_USERNAME, default=data.get(CONF_USERNAME, "user1")): str,
            vol.Optional(CONF_PASSWORD, default=data.get(CONF_PASSWORD, "")): str,
            vol.Required(
                "scan_interval_cgi",
                default=data.get("scan_interval_cgi", DEFAULT_SCAN_INTERVAL_CGI),
            ): vol.All(vol.Coerce(int), vol.Range(min=5, max=300)),
        }
    )


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the VARTA Storage config flow."""

    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()
            try:
                serial = await async_validate_modbus(self.hass, user_input)
            except (ModbusError, HomeAssistantError, TimeoutError, ValueError):
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(serial)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"VARTA Storage ({serial})",
                    data=user_input,
                )
        return self.async_show_form(step_id="user", data_schema=_schema(user_input), errors=errors)

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        entry = self._get_reconfigure_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_HOST] = user_input[CONF_HOST].strip()
            try:
                await async_validate_modbus(self.hass, user_input)
            except (ModbusError, HomeAssistantError, TimeoutError, ValueError):
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(entry, data=user_input)
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=_schema(entry.data),
            errors=errors,
        )
