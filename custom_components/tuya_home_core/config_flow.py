"""Config flow for Tuya Home Core."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant

from .api import TuyaHomeAPI
from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_REGION,
    DEFAULT_REGION,
    DOMAIN,
    REGIONS,
)


def _validate(hass: HomeAssistant, data: dict) -> dict | None:
    """Return None on success, or an errors dict on failure."""
    api = TuyaHomeAPI(data[CONF_API_KEY], data[CONF_API_SECRET], data[CONF_REGION])
    ok  = api.test_credentials()
    return None if ok else {"base": "invalid_auth"}


class TuyaHomeCoreConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single-step config flow: enter API key, secret, region."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_API_KEY])
            self._abort_if_unique_id_configured()

            errors_or_none = await self.hass.async_add_executor_job(
                _validate, self.hass, user_input
            )
            if errors_or_none is None:
                return self.async_create_entry(
                    title=f"Tuya ({user_input[CONF_REGION].upper()})",
                    data=user_input,
                )
            errors = errors_or_none

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_API_SECRET): str,
                vol.Required(CONF_REGION, default=DEFAULT_REGION): vol.In(REGIONS),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )
