"""Tuya Home Core — shared credential store for Tuya sub-integrations."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import TuyaHomeAPI
from .const import CONF_API_KEY, CONF_API_SECRET, CONF_REGION, CONF_UID, CONF_REFRESH_DAYS, DEFAULT_REFRESH_DAYS, DOMAIN
from .coordinator import TuyaHomeCoreCoordinator

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["button"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Tuya Home Core from a config entry."""
    api = TuyaHomeAPI(
        entry.data[CONF_API_KEY],
        entry.data[CONF_API_SECRET],
        entry.data[CONF_REGION],
    )

    refresh_days = entry.options.get(CONF_REFRESH_DAYS, DEFAULT_REFRESH_DAYS)
    coordinator  = TuyaHomeCoreCoordinator(hass, api, refresh_days)

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

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _LOGGER.info(
        "Tuya Home Core loaded: %d devices across %d area(s), refresh every %d day(s)",
        len(coordinator.data.get("devices", [])),
        len(set(coordinator.data.get("areas", {}).values())),
        refresh_days,
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
