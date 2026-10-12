from homeassistant.const import Platform

DOMAIN = "jullix"
DEFAULT_HOST = "http://jullix.local"
DEFAULT_SCAN_INTERVAL = 30
PLATFORMS: list[Platform] = [Platform.SENSOR]

# Config-entry / options keys
CONF_HOST = "host"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL = "scan_interval"

# Read endpoints polled by the sensor coordinator, keyed by the category used
# in entity unique_ids. The first five (EMS categories) MUST keep their names
# unchanged for backwards compatibility with existing entity ids/history.
SENSOR_ENDPOINTS: dict[str, str] = {
    "meter": "/api/ems/meter",
    "solar": "/api/ems/solar",
    "battery": "/api/ems/battery",
    "charger": "/api/ems/charger",
    "plug": "/api/ems/plug",
    "dsmr": "/api/dsmr/status",
    "inverter": "/api/inverter/status",
    "ethernet": "/api/ethernet/status",
    "wifi": "/api/wifi/status",
    "system": "/api/dashboard/system",
    "firmware": "/api/firmware/info",
}
