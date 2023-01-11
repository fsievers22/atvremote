"""Config flow for AndroidTV remote integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from atvremote.atvremote import ATVRemote

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# TODO adjust the data schema to the data that you need
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("host"): str,
    }
)

STEP_USER_DATA_SCHEMA_CODE = vol.Schema(
    {
        vol.Required("code"): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AndroidTV remote."""

    VERSION = 1

    def __init__(self) -> None:
        super().__init__()
        self.host: str = None
        self.atvremote: ATVRemote = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        if (host := user_input.get("host")) is not None:
            self.host = host
            logging.info(f"Connecting to host: {host}")
            self.atvremote = ATVRemote(host)
            if not await self.atvremote.start_pairing():
                errors["base"] = "cannot_connect"
                return self.async_show_form(
                    step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
                )
            await self.async_set_unique_id(self.atvremote.unique_id)
            self._abort_if_unique_id_configured()
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA_CODE, errors=errors
            )
        if not await self.atvremote.finish_pairing(user_input["code"]):
            errors["base"] = "invalid_auth"
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA_CODE, errors=errors
            )
        return self.async_create_entry(
            title="AndroidTV remote", data={"host": self.host, "unique_id": self.atvremote.unique_id}
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
