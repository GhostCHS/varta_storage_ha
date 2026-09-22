"""Register models for VARTA storage systems."""

from __future__ import annotations

from enum import IntEnum

from modbus_connection.model import Component, enum, gauge, integer, string, uint32


def validate_maximum_discharging_power(value: int) -> int:
    """Validate maximum discharge power."""
    value = int(value)
    if value != 0 and value > -500:
        raise ValueError("Maximum discharge power must be 0 W or below -500 W")
    return value


def validate_maximum_charging_power(value: int) -> int:
    """Validate maximum charge power."""
    value = int(value)
    if value != 0 and value < 500:
        raise ValueError("Maximum charge power must be 0 W or above 500 W")
    return value


class VartaState(IntEnum):
    """Operating state reported by register 1065."""

    BUSY = 0
    RUN = 1
    CHARGE = 2
    DISCHARGE = 3
    STANDBY = 4
    ERROR = 5
    SERVICE = 6
    ISLANDING = 7


class Identity(Component):
    """Identity and software information."""

    register_ranges = ((1000, 1064),)
    ems_software = string(1000, 17)
    ens_software = string(1017, 17)
    software = string(1034, 17)
    table_version = integer(1051, signed=False)
    serial_number = string(1054, 10)
    installed_battery_modules = integer(1064, signed=False)


class Battery(Component):
    """Battery operating measurements."""

    register_ranges = ((1065, 1075),)
    state = enum(1065, VartaState)
    active_power = integer(1066, signed=True, unit="W")
    apparent_power = integer(1067, signed=True, unit="VA")
    state_of_charge = integer(1068, signed=False, unit="%")
    ac_to_dc_energy = uint32(1069, word_order="little", unit="Wh")
    installed_capacity = gauge(1071, 10, signed=False, unit="Wh")
    error_code = gauge(1072, 10, signed=False)
    external_control_timeout = integer(1073, signed=False, unit="s")
    maximum_discharging_power = integer(
        1074, signed=True, unit="W", writable=validate_maximum_discharging_power
    )
    maximum_charging_power = integer(
        1075, signed=True, unit="W", writable=validate_maximum_charging_power
    )

    @property
    def charging_power(self) -> int | None:
        """Charging power as a positive value."""
        if self.active_power is None:
            return None
        return max(self.active_power, 0)

    @property
    def discharging_power(self) -> int | None:
        """Discharging power as a positive value."""
        if self.active_power is None:
            return None
        return max(-self.active_power, 0)


class Grid(Component):
    """Grid-side measurements."""

    register_ranges = ((1078, 1078),)
    power = integer(1078, signed=True, unit="W")
