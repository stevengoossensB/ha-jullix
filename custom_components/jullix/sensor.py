"""Platform for Jullix sensors."""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta, timezone

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

ICONS: dict[str, str] = {
    "meter": "mdi:flash",
    "solar": "mdi:solar-power",
    "battery": "mdi:battery",
    "charger": "mdi:ev-station",
    "plug": "mdi:power-plug",
}

_LOGGER = logging.getLogger(__name__)
_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "sensor_config.json")

try:
    with open(_CONFIG_PATH, encoding="utf-8") as file:
        SENSOR_CONFIG = json.load(file)
except FileNotFoundError:
    _LOGGER.error("sensor_config.json not found at %s", _CONFIG_PATH)
    SENSOR_CONFIG = {}


def _sample_device_id(category: str, sample: dict) -> str:
    """Return a stable, unique device identifier for a data sample.

    Solar payloads can contain multiple inverters with the same ``id`` but
    different ``localid`` values (e.g. ``A01``, ``T01``).  For solar entries
    both fields are combined so every inverter gets its own identity.  For all
    other categories the existing ``id`` / ``meter`` / category fallback is
    preserved.
    """
    if category == "solar":
        sid = sample.get("id")
        lid = sample.get("localid")
        if sid and lid:
            return f"{sid}_{lid}"
        return lid or sid or category
    return sample.get("id") or sample.get("meter") or category


def _flatten(obj, parent_key: str = "", out: dict | None = None) -> dict:
    out = {} if out is None else out
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_key = f"{parent_key}_{key}" if parent_key else key
            _flatten(value, new_key, out)
    else:
        out[parent_key] = obj
    return out


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up Jullix sensors from a config entry."""
    session = async_get_clientsession(hass)
    host = hass.data[DOMAIN][entry.entry_id]["host"]

    async def fetch_json(endpoint: str):
        try:
            async with asyncio.timeout(10):
                response = await session.get(f"{host}{endpoint}")
                response.raise_for_status()
                return await response.json()
        except Exception as err:
            _LOGGER.error("Error fetching %s: %s", endpoint, err)
            return None

    async def _update():
        return {
            key: await fetch_json(f"/api/ems/{key}")
            for key in ["meter", "solar", "battery", "charger", "plug"]
        }

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="jullix",
        update_method=_update,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()

    entities = []
    for category, payload in coordinator.data.items():
        if not payload:
            continue
        samples = payload if isinstance(payload, list) else [payload]
        for sample in samples:
            device_id = _sample_device_id(category, sample)
            name_base = sample.get("device", f"Jullix {category.title()}")
            flat = _flatten(sample)
            for key in flat:
                entities.append(
                    JullixSensor(coordinator, category, key, device_id, name_base)
                )

    async_add_entities(entities)


class JullixSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, category, key, device_id, name_base):
        super().__init__(coordinator)
        self._attr_icon = ICONS.get(category)
        self._category = category
        self._key = key
        self._device_id = device_id
        self._name_base = name_base
        self._attr_name = f"{name_base} {key.replace('_', ' ').title()}"
        self._attr_unique_id = f"jullix_{category}_{device_id}_{key}"

        config = SENSOR_CONFIG.get(category, {}).get(key, {})
        self._attr_native_unit_of_measurement = config.get("unit_of_measurement")
        self._attr_device_class = config.get("device_class")
        self._attr_state_class = config.get("state_class")

    @property
    def device_info(self) -> DeviceInfo:
        """Group sensors by physical device."""
        return DeviceInfo(
            identifiers={(DOMAIN, f"{self._category}_{self._device_id}")},
            name=self._name_base,
            manufacturer="Jullix",
            model=self._category.title(),
        )

    @property
    def native_value(self):
        data = self.coordinator.data.get(self._category)
        if not data:
            return None
        if isinstance(data, list):
            sample = next(
                (
                    candidate
                    for candidate in data
                    if _sample_device_id(self._category, candidate) == self._device_id
                ),
                data[0],
            )
        else:
            sample = data

        flat = _flatten(sample)
        value = flat.get(self._key)

        if (
            self._category == "meter"
            and self._key in ("time", "captar_month_max_time")
            and value
        ):
            try:
                dt = datetime.strptime(str(value), "%y%m%d%H%M%S")
                return dt.replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                _LOGGER.error(
                    "Unable to parse timestamp %s for sensor %s", value, self._key
                )

        if isinstance(value, (int, float)):
            return round(value, 2)

        return value

    @property
    def icon(self) -> str | None:
        """Return mdi: icon based on category."""
        return ICONS.get(self._category)
