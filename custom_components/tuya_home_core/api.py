"""Tuya Cloud API wrapper for Tuya Home Core."""

from __future__ import annotations

import logging
from typing import Any

import tinytuya

_LOGGER = logging.getLogger(__name__)


class TuyaHomeAPI:
    """Authenticated Tuya Cloud client with area/device helpers."""

    def __init__(self, api_key: str, api_secret: str, region: str, uid: str = "") -> None:
        self._api_key    = api_key
        self._api_secret = api_secret
        self._region     = region
        self._uid        = uid
        self._client: tinytuya.Cloud | None = None

    # ── Client ────────────────────────────────────────────────────────────────

    def _get_client(self) -> tinytuya.Cloud:
        if self._client is None:
            self._client = tinytuya.Cloud(
                apiRegion=self._region,
                apiKey=self._api_key,
                apiSecret=self._api_secret,
            )
        return self._client

    @property
    def client(self) -> tinytuya.Cloud:
        return self._get_client()

    # ── Validation ────────────────────────────────────────────────────────────

    def get_uid(self) -> str:
        """Return the Tuya account UID — needed for MQTT subscriptions."""
        try:
            devices = self.get_devices()
            return next((d.get("uid", "") for d in devices if d.get("uid")), "")
        except Exception:
            return ""

    def test_credentials(self) -> bool:
        """Return True if credentials are valid (makes one lightweight API call)."""
        try:
            result = self._get_client().getdevices()
            if isinstance(result, dict):
                return result.get("success", False)
            # getdevices() may return a list on success
            return isinstance(result, list)
        except Exception as err:
            _LOGGER.debug("Credential test failed: %s", err)
            return False

    # ── Devices ───────────────────────────────────────────────────────────────

    def get_devices(self) -> list[dict[str, Any]]:
        """Return all devices from Tuya Cloud. Returns [] on error.

        With a stored uid, calls /v1.3/iot-03/devices directly — works with both
        Auto Link and Custom Link projects. Falls back to tinytuya's getdevices()
        (which uses /v1.0/iot-01/associated-users/devices and only works with Auto Link).
        """
        if self._uid:
            try:
                resp = self._get_client().cloudrequest(
                    "/v1.3/iot-03/devices",
                    query={"source_type": "tuyaUser", "source_id": self._uid, "page_size": "75"},
                )
                if resp and resp.get("success"):
                    inner = resp.get("result", {})
                    devices = inner.get("list") or inner.get("devices") or []
                    if isinstance(devices, list):
                        _LOGGER.debug("get_devices (uid path): %d devices", len(devices))
                        return devices
            except Exception as err:
                _LOGGER.debug("get_devices uid-path failed: %s — falling back", err)

        try:
            result = self._get_client().getdevices(verbose=True)
            if isinstance(result, dict) and result.get("success"):
                return result.get("result", [])
            if isinstance(result, list):
                return result
        except Exception as err:
            _LOGGER.warning("get_devices failed: %s", err)
        return []

    # ── Areas (Tuya homes → area names) ───────────────────────────────────────

    def get_area_map(self, devices: list[dict[str, Any]]) -> dict[str, str]:
        """
        Build {device_id: area_name} from Tuya home management.
        Uses the user's Tuya home names; falls back to empty string if unavailable.
        """
        uid = next((d.get("uid") for d in devices if d.get("uid")), None) or self._uid or None
        if not uid:
            return {}

        try:
            homes_resp = self._get_client().cloudrequest(f"/v1.0/users/{uid}/homes")
        except Exception as err:
            _LOGGER.warning("homes API failed: %s", err)
            return {}

        if not homes_resp.get("success"):
            _LOGGER.debug("homes API unavailable: %s", homes_resp.get("msg", ""))
            return {}

        area_map: dict[str, str] = {}
        for home in homes_resp.get("result", []):
            home_id   = home["home_id"]
            home_name = home.get("name", "")
            try:
                devs_resp = self._get_client().cloudrequest(f"/v1.0/homes/{home_id}/devices")
            except Exception as err:
                _LOGGER.warning("home devices API failed for %s: %s", home_id, err)
                continue
            if not devs_resp.get("success"):
                continue
            for d in devs_resp.get("result", []):
                area_map[d["id"]] = home_name

        return area_map

    # ── Generic request passthrough ───────────────────────────────────────────

    def request(self, path: str, action: str = "GET", body: dict | None = None) -> dict:
        """Pass-through for sub-integrations that need direct API access."""
        return self._get_client().cloudrequest(path, action=action, post=body)
