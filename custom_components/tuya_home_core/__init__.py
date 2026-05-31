"""Tuya Home Core — shared credential store for Tuya sub-integrations."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import TuyaHomeAPI
from .const import CONF_API_KEY, CONF_API_SECRET, CONF_REGION, CONF_UID, DOMAIN
from .coordinator import TuyaHomeCoreCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tuya Home Core from a config entry."""
    api = TuyaHomeAPI(
        entry.data[CONF_API_KEY],
        entry.data[CONF_API_SECRET],
        entry.data[CONF_REGION],
    )

    coordinator = TuyaHomeCoreCoordinator(hass, api)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(
            f"Tuya API unreachable at startup: {err}"
        ) from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "api":         api,
        "uid":         entry.data.get(CONF_UID, ""),
    }

    _LOGGER.info(
        "Tuya Home Core loaded: %d devices across %d area(s)",
        len(coordinator.data.get("devices", [])),
        len(set(coordinator.data.get("areas", {}).values())),
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True
