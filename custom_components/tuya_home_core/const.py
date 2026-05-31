"""Constants for Tuya Home Core."""

DOMAIN = "tuya_home_core"

CONF_API_KEY    = "api_key"
CONF_API_SECRET = "api_secret"
CONF_REGION     = "region"
CONF_UID        = "uid"          # Tuya account user ID (for MQTT, auto-detected but editable)

REGIONS = ["eu", "us", "cn", "in"]
DEFAULT_REGION = "eu"

# How often to refresh the device/area list from Tuya Cloud
COORDINATOR_UPDATE_INTERVAL_MINUTES = 60
