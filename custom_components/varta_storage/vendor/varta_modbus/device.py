"""Top-level VARTA storage device."""

from __future__ import annotations

from modbus_connection import ModbusUnit
from modbus_connection.model import Device, UpdateReport

from .external_control import ExternalControl
from .model import Battery, Grid, Identity

VARTA_TIMEOUT = 3.0
VARTA_MESSAGE_SPACING = 0.250
VARTA_CONNECT_DELAY = 1.0


class VartaStorage(Device):
    """A VARTA storage system addressed as one Modbus unit."""

    def __init__(self, unit: ModbusUnit) -> None:
        super().__init__(unit)

        set_message_spacing = getattr(unit, "set_message_spacing", None)
        if set_message_spacing is not None:
            set_message_spacing(VARTA_MESSAGE_SPACING)

        unit.require_timeout(VARTA_TIMEOUT)
        unit.require_connect_delay(VARTA_CONNECT_DELAY)

        self.identity = Identity(unit)
        self.battery = Battery(unit)
        self.grid = Grid(unit)
        self.external_control = ExternalControl(self.battery)

    async def _async_setup(self) -> None:
        """Read stable identity data before normal polling."""
        await self.identity.async_update()

    async def async_update_readings(self) -> UpdateReport:
        """Refresh changing measurements."""
        return await self.async_poll(("battery", "grid"))

    async def async_update_identity(self) -> UpdateReport:
        """Refresh identity and software information."""
        return await self.async_poll(("identity",))

    async def async_update(self) -> UpdateReport:
        """Refresh all exposed components."""
        report = await self.async_poll(("battery", "grid"))
        return await self.async_poll(("identity",), report=report)

    async def async_validate(self) -> None:
        """Verify that the target answers with VARTA identity data."""
        await self.async_ensure_setup()
        if not self.identity.serial_number and not self.identity.table_version:
            raise ValueError("Device answered but did not expose a VARTA identity")
