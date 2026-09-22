"""Coordinators for VARTA Modbus and WebIF data."""

from __future__ import annotations

from datetime import timedelta
import logging

from aiohttp import ClientSession
from modbus_connection import ModbusError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import VartaClient
from .vendor.varta_modbus import VartaStorage

_LOGGER = logging.getLogger(__name__)


class VartaModbusCoordinator(DataUpdateCoordinator[None]):
    """Poll the VARTA Modbus device."""

    def __init__(self, hass: HomeAssistant, device: VartaStorage, interval: int = 1) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="VARTA Modbus",
            update_interval=timedelta(seconds=interval),
        )
        self.device = device

    async def _async_update_data(self) -> None:
        try:
            await self.device.async_update_readings()
        except ModbusError as err:
            raise UpdateFailed(str(err)) from err


class VartaWebCoordinator(DataUpdateCoordinator[dict]):
    """Poll the VARTA WebIF while retaining the last valid snapshot."""

    def __init__(
        self,
        hass: HomeAssistant,
        session: ClientSession,
        host: str,
        username: str,
        password: str,
        interval: int = 10,
    ) -> None:
        super().__init__(
            hass,
            logger=_LOGGER,
            name="VARTA WebIF",
            update_interval=timedelta(seconds=interval),
        )
        self.client = VartaClient(session, host, username, password)
        self._last_good_data: dict | None = None

    async def _async_update_data(self) -> dict:
        try:
            data = await self.client.read_all()
            self._last_good_data = data
            return data
        except Exception as err:
            if self._last_good_data is not None:
                _LOGGER.debug("Temporary VARTA WebIF failure; keeping last valid values: %s", err)
                return self._last_good_data
            raise UpdateFailed(str(err)) from err


def create_web_coordinator(
    hass: HomeAssistant,
    host: str,
    username: str,
    password: str,
    interval: int,
) -> VartaWebCoordinator:
    """Create the WebIF coordinator using HA's shared HTTP session."""
    return VartaWebCoordinator(
        hass,
        async_get_clientsession(hass),
        host,
        username,
        password,
        interval,
    )
