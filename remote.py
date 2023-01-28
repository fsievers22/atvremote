"""Platform for an AndroidTV integration"""
from typing import Iterable
import asyncio
from homeassistant.components.remote import (
    RemoteEntity,
    RemoteEntityFeature,
    ATTR_HOLD_SECS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from py_atvremote.py_atvremote import ATVRemote
from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add cover for passed config_entry in HA."""
    # The device is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function
    atv_remote: ATVRemote = hass.data[DOMAIN][config_entry.entry_id]
    # Add all entities to HA
    async_add_entities([AndroidTVRemote(atv_remote)])


class AndroidTVRemote(RemoteEntity):
    """Represantation of an AndroidTV remote"""

    should_poll = False
    supported_features = RemoteEntityFeature.ACTIVITY
    has_entity_name = True
    name = None

    def __init__(self, atv_remote: ATVRemote) -> None:
        self._atv_remote = atv_remote
        """Initialize remote entity"""

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self._atv_remote.unique_id)
            },
            name=f"{self._atv_remote.device_info.vendor}_{self._atv_remote.device_info.model}",
            unique_id=self._atv_remote.unique_id,
            manufacturer=self._atv_remote.device_info.vendor,
            model=self._atv_remote.device_info.model,
            sw_version=self._atv_remote.device_info.app_version,
        )

    @property
    def unique_id(self) -> str:
        return self._atv_remote.unique_id

    @property
    def current_activity(self) -> str:
        """Return current activity of AndroidTV"""
        return self._atv_remote.get_activity()

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        await self._atv_remote.establish_connection(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        self._atv_remote.disconnect()

    async def async_send_command(self, command: Iterable[str], **kwargs):
        """Send commands to a device."""
        for single_command in command:
            if kwargs[ATTR_HOLD_SECS] is not None:
                await self._atv_remote.key_down(single_command)
                await asyncio.sleep(kwargs[ATTR_HOLD_SECS])
                await self._atv_remote.key_up(single_command)
                return
            await self._atv_remote.key_press(single_command)
