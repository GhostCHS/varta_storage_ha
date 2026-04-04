"""Config flow for VARTA Storage integration."""

from __future__ import annotations

from typing import Any

from vartastorage import vartastorage
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DEFAULT_SCAN_INTERVAL_CGI,
    DEFAULT_SCAN_INTERVAL_MODBUS,
    DOMAIN,
    LOGGER,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=502): int,
        vol.Optional("scan_interval_modbus", default=DEFAULT_SCAN_INTERVAL_MODBUS): int,
        vol.Required("cgi", default=True): bool,
        vol.Optional("host_cgi", default=""): str,
        vol.Optional(CONF_USERNAME, default="user1"): str,
        vol.Optional(CONF_PASSWORD, default=""): str,
        vol.Optional("scan_interval_cgi", default=DEFAULT_SCAN_INTERVAL_CGI): int,
    }
)


class VartaHub:
    """Provide methods for GUI configuration."""

    def __init__(
        self,
        host: str,
        port: int,
        scan_interval_modbus: int,
        cgi: bool,
        scan_interval_cgi: int,
        host_cgi: str | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Initialize."""
        self.host = host
        self.port = port
        self.serial = ""
        self.scan_interval_modbus = scan_interval_modbus
        self.cgi = cgi
        self.host_cgi = host_cgi
        self.username = username
        self.password = password
        self.scan_interval_cgi = scan_interval_cgi

    def test_connection(self) -> bool:
        """Test a connection to the VARTA device."""
        varta = vartastorage.VartaStorage(
            self.host,
            self.port,
            self.cgi,
            self.username,
            self.password,
        )
        try:
            self.serial = varta.modbus_client.get_serial()
            return True
        except Exception:
            return False


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    hub = VartaHub(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        scan_interval_modbus=data["scan_interval_modbus"],
        cgi=data["cgi"],
        scan_interval_cgi=data["scan_interval_cgi"],
        host_cgi=data["host_cgi"],
        username=data[CONF_USERNAME],
        password=data[CONF_PASSWORD],
    )

    if not await hass.async_add_executor_job(hub.test_connection):
        raise CannotConnect

    return {
        "title": f"{data[CONF_HOST]} (S/N: {hub.serial})",
        "serial": hub.serial,
        "scan_interval_modbus": hub.scan_interval_modbus,
        "scan_interval_cgi": hub.scan_interval_cgi,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VARTA Storage."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors: dict[str, str] = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except Exception as err:
            LOGGER.exception("Unexpected exception during config flow: %s", err)
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(info["serial"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for VARTA Storage."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        current = self.config_entry.data.copy()
        current.update(self.config_entry.options)

        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=user_input,
                options=self.config_entry.options,
            )
            return self.async_create_entry(
                title=self.config_entry.title,
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current.get(CONF_HOST, "")): str,
                vol.Required(CONF_PORT, default=current.get(CONF_PORT, 502)): int,
                vol.Optional(
                    "scan_interval_modbus",
                    default=current.get(
                        "scan_interval_modbus", DEFAULT_SCAN_INTERVAL_MODBUS
                    ),
                ): int,
                vol.Required("cgi", default=current.get("cgi", True)): bool,
                vol.Optional("host_cgi", default=current.get("host_cgi", "")): str,
                vol.Optional(
                    CONF_USERNAME,
                    default=current.get(CONF_USERNAME, "user1"),
                ): str,
                vol.Optional(
                    CONF_PASSWORD,
                    default=current.get(CONF_PASSWORD, ""),
                ): str,
                vol.Optional(
                    "scan_interval_cgi",
                    default=current.get(
                        "scan_interval_cgi", DEFAULT_SCAN_INTERVAL_CGI
                    ),
                ): int,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
