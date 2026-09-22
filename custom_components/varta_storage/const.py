"""Constants for the unified VARTA Storage integration."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Final

from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.const import PERCENTAGE, UnitOfEnergy, UnitOfPower, UnitOfTime

DOMAIN = "varta_storage"
LOGGER = logging.getLogger(__name__)

CONF_UNIT_ID = "unit_id"
DEFAULT_UNIT_ID = 1
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL_MODBUS = 1
DEFAULT_SCAN_INTERVAL_CGI = 10


@dataclass(frozen=True, kw_only=True)
class VartaSensorEntityDescription(SensorEntityDescription):
    """Describe a VARTA sensor."""

    source: str = "modbus"
    source_key: str = ""


SENSORS: Final[tuple[VartaSensorEntityDescription, ...]] = (
    VartaSensorEntityDescription(
        key="state",
        name="Betriebsstatus",
        source_key="state",
    ),
    VartaSensorEntityDescription(
        key="active_power",
        name="Batterieleistung",
        source_key="active_power",
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    VartaSensorEntityDescription(
        key="charging_power",
        name="Ladeleistung",
        source_key="charging_power",
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    VartaSensorEntityDescription(
        key="discharging_power",
        name="Entladeleistung",
        source_key="discharging_power",
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    VartaSensorEntityDescription(
        key="soc",
        name="Ladezustand",
        source_key="state_of_charge",
        native_unit_of_measurement=PERCENTAGE,
    ),
    VartaSensorEntityDescription(
        key="grid_power",
        name="Netzleistung",
        source_key="grid_power",
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    VartaSensorEntityDescription(
        key="installed_capacity",
        name="Batteriekapazität",
        source_key="installed_capacity",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    VartaSensorEntityDescription(
        key="error_code",
        name="Fehlercode",
        source_key="error_code",
    ),
    VartaSensorEntityDescription(
        key="external_control_timeout",
        name="Watchdog",
        source_key="external_control_timeout",
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    VartaSensorEntityDescription(
        key="installed_modules",
        name="Batteriemodule",
        source_key="installed_battery_modules",
    ),
    VartaSensorEntityDescription(
        key="ems_software",
        name="EMS Software",
        source_key="ems_software",
    ),
    VartaSensorEntityDescription(
        key="ens_software",
        name="ENS Software",
        source_key="ens_software",
    ),
    VartaSensorEntityDescription(
        key="software",
        name="VARTA Software",
        source_key="software",
    ),
    VartaSensorEntityDescription(
        key="ac_to_dc_energy",
        name="Geladene Energie",
        source_key="ac_to_dc_energy",
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
    ),
    VartaSensorEntityDescription(
        key="production_power",
        name="Produktionsleistung",
        source="web",
        source_key="production_power",
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    VartaSensorEntityDescription(
        key="house_consumption",
        name="Hausverbrauch",
        source="web",
        source_key="house_consumption",
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    VartaSensorEntityDescription(
        key="grid_import_power",
        name="Netzbezug",
        source="web",
        source_key="grid_import_power",
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    VartaSensorEntityDescription(
        key="grid_export_power",
        name="Netzeinspeisung",
        source="web",
        source_key="grid_export_power",
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    VartaSensorEntityDescription(
        key="battery_charge_power_web",
        name="Ladeleistung (WebIF)",
        source="web",
        source_key="battery_charge_power",
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    VartaSensorEntityDescription(
        key="battery_discharge_power_web",
        name="Entladeleistung (WebIF)",
        source="web",
        source_key="battery_discharge_power",
        native_unit_of_measurement=UnitOfPower.WATT,
    ),
    VartaSensorEntityDescription(
        key="charge_cycles",
        name="Ladezyklen",
        source="web",
        source_key="charge_cycles",
    ),
    VartaSensorEntityDescription(
        key="active_errors",
        name="Aktive Fehler",
        source="web",
        source_key="active_errors",
    ),
)
