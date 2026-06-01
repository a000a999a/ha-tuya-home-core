"""Config flow + options flow + re-auth flow for Tuya Home Core."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from .api import TuyaHomeAPI
from .const import (
    CONF_API_KEY,
    CONF_API_SECRET,
    CONF_REFRESH_DAYS,
    CONF_REGION,
    CONF_UID,
    DEFAULT_REFRESH_DAYS,
    DEFAULT_REGION,
    DOMAIN,
    REGIONS,
)


def _build_schema(defaults: dict | None = None) -> vol.Schema:
    d = defaults or {}
    return vol.Schema({
        vol.Required(CONF_API_KEY,    default=d.get(CONF_API_KEY, "")): str,
        vol.Required(CONF_API_SECRET, default=d.get(CONF_API_SECRET, "")):
            selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)),
        vol.Required(CONF_REGION,     default=d.get(CONF_REGION, DEFAULT_REGION)):
            vol.In(REGIONS),
        vol.Optional(CONF_UID,        default=d.get(CONF_UID, "")):
            selector.TextSelector(selector.TextSelectorConfig(
                type=selector.TextSelectorType.TEXT
            )),
    })


def _validate_and_fetch_uid(data: dict) -> tuple[bool, str]:
    """
    Validate credentials with a live API call.
    Returns (is_valid, uid).
    Auto-detects UID if not provided by user.
    """
    api = TuyaHomeAPI(data[CONF_API_KEY], data[CONF_API_SECRET], data[CONF_REGION])
    if not api.test_credentials():
        return False, ""
    uid = data.get(CONF_UID, "").strip() or api.get_uid()
    return True, uid


class TuyaHomeCoreConfigFlow(ConfigFlow, domain=DOMAIN):
    """Single-step setup: API key, secret, region, optional UID."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_API_KEY])
            self._abort_if_unique_id_configured()

            valid, uid = await self.hass.async_add_executor_job(
                _validate_and_fetch_uid, user_input
            )
            if not valid:
                errors["base"] = "invalid_auth"
            else:
                data = {**user_input, CONF_UID: uid}
                return self.async_create_entry(
                    title=f"Tuya ({user_input[CONF_REGION].upper()})",
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(user_input),
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict
    ) -> ConfigFlowResult:
        """Triggered automatically when API returns auth failure."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        reauth_entry = self._get_reauth_entry()

        if user_input is not None:
            valid, uid = await self.hass.async_add_executor_job(
                _validate_and_fetch_uid, user_input
            )
            if not valid:
                errors["base"] = "invalid_auth"
            else:
                data = {**user_input, CONF_UID: uid}
                self.hass.config_entries.async_update_entry(reauth_entry, data=data)
                await self.hass.config_entries.async_reload(reauth_entry.entry_id)
                return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=_build_schema(reauth_entry.data),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return TuyaHomeCoreOptionsFlow(config_entry)


class TuyaHomeCoreOptionsFlow(OptionsFlow):
    """Options flow: update API credentials or UID without re-adding."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            valid, uid = await self.hass.async_add_executor_job(
                _validate_and_fetch_uid, user_input
            )
            if not valid:
                errors["base"] = "invalid_auth"
            else:
                new_data = {**user_input, CONF_UID: uid}
                self.hass.config_entries.async_update_entry(self._entry, data=new_data)
                return self.async_create_entry(
                    data={CONF_REFRESH_DAYS: int(user_input[CONF_REFRESH_DAYS])}
                )

        current_refresh = self._entry.options.get(CONF_REFRESH_DAYS, DEFAULT_REFRESH_DAYS)
        defaults = {**self._entry.data, CONF_REFRESH_DAYS: current_refresh}

        schema = vol.Schema({
            **_build_schema(self._entry.data).schema,
            vol.Optional(CONF_REFRESH_DAYS, default=current_refresh):
                selector.NumberSelector(selector.NumberSelectorConfig(
                    min=1, max=30, step=1,
                    mode=selector.NumberSelectorMode.SLIDER,
                    unit_of_measurement="days",
                )),
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
            description_placeholders={
                "current_region": self._entry.data.get(CONF_REGION, "").upper(),
                "current_uid":    self._entry.data.get(CONF_UID, "(auto-detected)"),
            },
        )
