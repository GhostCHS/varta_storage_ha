"""VARTA external battery power control."""

from __future__ import annotations

import asyncio
import logging

from .model import Battery

_LOGGER = logging.getLogger(__name__)
REFRESH_INTERVAL = 60.0


class ExternalControl:
    """Maintain VARTA external battery power limits."""

    def __init__(self, battery: Battery) -> None:
        self._battery = battery
        self._maximum_discharging_power: int | None = None
        self._maximum_charging_power: int | None = None
        self._task: asyncio.Task[None] | None = None
        self._lock = asyncio.Lock()

    @property
    def active(self) -> bool:
        return self._maximum_discharging_power is not None or self._maximum_charging_power is not None

    async def async_set_discharging_power(self, value: int) -> None:
        value = int(value)
        if value != 0 and value > -500:
            raise ValueError("VARTA accepts discharge limits of 0 W or below -500 W.")
        async with self._lock:
            self._maximum_discharging_power = value
            await self._battery.write("maximum_discharging_power", value)
            self._ensure_watchdog()

    async def async_set_charging_power(self, value: int) -> None:
        value = int(value)
        if value != 0 and value < 500:
            raise ValueError("VARTA accepts charge limits of 0 W or above 500 W.")
        async with self._lock:
            self._maximum_charging_power = value
            await self._battery.write("maximum_charging_power", value)
            self._ensure_watchdog()

    def _ensure_watchdog(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._async_watchdog())

    async def _async_watchdog(self) -> None:
        while self.active:
            try:
                await asyncio.sleep(REFRESH_INTERVAL)
                async with self._lock:
                    if self._maximum_discharging_power is not None:
                        await self._battery.write("maximum_discharging_power", self._maximum_discharging_power)
                    if self._maximum_charging_power is not None:
                        await self._battery.write("maximum_charging_power", self._maximum_charging_power)
            except asyncio.CancelledError:
                raise
            except Exception:
                _LOGGER.exception("Failed to refresh VARTA external power limits")

    async def async_stop(self) -> None:
        self._maximum_discharging_power = None
        self._maximum_charging_power = None
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None
