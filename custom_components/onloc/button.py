import logging

from config.custom_components.onloc.coordinator import OnlocCoordinator
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    await coord.async_refresh()

    entities = [RingButton(coord, dev_id, dev) for dev_id, dev in coord.devices.items()]
    async_add_entities(entities, True)


class RingButton(CoordinatorEntity[OnlocCoordinator], ButtonEntity):
    _attr_has_entity_name = True

    def __init__(self, coord, device_id: str, device: dict):
        super().__init__(coord)
        self.device_id = device_id
        self.device = device

        self._attr_unique_id = f"{DOMAIN}_{device_id}_ring"
        self._attr_name = "Ring"
        self._attr_icon = "mdi:bell-ring"

        # Link to the same device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
        )

    async def async_press(self) -> None:
        try:
            await self.coordinator.hub.ring_device(self.device_id)
            _LOGGER.info("Sent ring command to device %s", self.device_id)
        except Exception as error:
            _LOGGER.error(
                "Failed to send ring command to %s: %s", self.device_id, error
            )
            raise
