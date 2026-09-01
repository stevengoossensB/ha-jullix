from homeassistant.const import Platform

DOMAIN = "jullix"
DEFAULT_HOST = "http://jullix.local"
DEFAULT_SCAN_INTERVAL = 30
PLATFORMS: list[Platform] = [Platform.SENSOR]
