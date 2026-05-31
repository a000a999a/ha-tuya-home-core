"""DataUpdateCoordinator for Tuya Home Core."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import TuyaHomeAPI
from .const import COORDINATOR_UPDATE_INTERVAL_MINUTES, DOMAIN

_LOGGER = logging.getLogger(__name__)


class TuyaHomeCoreCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """
    Fetches and caches Tuya device list and area map once per hour.

    data layout:
      {
        "devices":  [list of raw Tuya device dicts],
        "areas":    {device_id: area_name},
      }

    Sub-integrations access this via:
      hass.data[DOMAIN][entry_id]["coordinator"]
    """

    def __init__(self, hass: HomeAssistant, api: TuyaHomeAPI) -> None:
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=COORDINATOR_UPDATE_INTERVAL_MINUTES),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            devices = await self.hass.async_add_executor_job(self.api.get_devices)
            areas   = await self.hass.async_add_executor_job(self.api.get_area_map, devices)
        except Exception as err:
            # Keep stale data rather than failing — do not raise if we have data already
            if self.data:
                _LOGGER.warning("Tuya refresh failed, keeping stale data: %s", err)
                return self.data
            raise UpdateFailed(f"Tuya API error: {err}") from err

        _LOGGER.debug("Tuya coordinator refreshed: %d devices, %d areas", len(devices), len(areas))
        return {"devices": devices, "areas": areas}
