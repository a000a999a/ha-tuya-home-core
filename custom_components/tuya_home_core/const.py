"""Constants for Tuya Home Core."""

DOMAIN = "tuya_home_core"

CONF_API_KEY      = "api_key"
CONF_API_SECRET   = "api_secret"
CONF_REGION       = "region"
CONF_UID          = "uid"          # Tuya account user ID (for MQTT, auto-detected but editable)
CONF_PROJECT_NAME = "project_name" # Optional friendly label shown in sub-integration selectors

CONF_REFRESH_DAYS    = "refresh_days"
DEFAULT_REFRESH_DAYS = 14

REGIONS = ["eu", "us", "cn", "in"]
DEFAULT_REGION = "eu"
