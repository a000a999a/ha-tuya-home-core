"""Refresh Devices button for Tuya Home Core."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import TuyaHomeCoreCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([RefreshDevicesButton(entry, coordinator)])


class RefreshDevicesButton(ButtonEntity):
    """Manually triggers a full device list + area map refresh from Tuya Cloud."""

    _attr_has_entity_name   = True
    _attr_name              = "Refresh Devices"
    _attr_icon              = "mdi:refresh"
    _attr_entity_category   = EntityCategory.DIAGNOSTIC

    def __init__(self, entry: ConfigEntry, coordinator: TuyaHomeCoreCoordinator) -> None:
        self._coordinator    = coordinator
        self._attr_unique_id = f"{entry.entry_id}_refresh_devices"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Tuya Home Core",
            manufacturer="Tuya",
        )

    async def async_press(self) -> None:
        await self._coordinator.async_refresh()
        _LOGGER.info("Device list refreshed manually")
