import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Creates the button entities for devices that support them."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_refresh()

    entities = []
    for device_id, device in coordinator.devices.items():
        can_ring = device.get("can_ring")
        if can_ring:
            entities.append(RingButton(coordinator, device_id, device))
        can_lock = device.get("can_lock")
        if can_lock:
            entities.append(LockButton(coordinator, device_id, device))

    async_add_entities(entities, True)


class RingButton(ButtonEntity):
    """Button used to ring a device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id: str, device: dict):
        """Initializes the button."""

        super().__init__()
        self.coordinator = coordinator

        self.device_id = device_id
        self.device = device

        self._attr_unique_id = f"{DOMAIN}_{device_id}_ring"
        self._attr_name = "Ring"
        self._attr_icon = "mdi:bell-ring"

        # Link to the same device
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})

    async def async_press(self) -> None:
        """Triggered when the button is pressed.

        Sends a request to ring the device.
        """

        try:
            await self.coordinator.hub.ring_device(self.device_id)
            _LOGGER.info("Sent ring command to device %s", self.device_id)
        except Exception as error:
            _LOGGER.error(
                "Failed to send ring command to %s: %s", self.device_id, error
            )
            raise


class LockButton(ButtonEntity):
    """Button used to lock a device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, device_id: str, device: dict):
        """Initializes the button."""

        super().__init__()
        self.coordinator = coordinator

        self.device_id = device_id
        self.device = device

        self._attr_unique_id = f"{DOMAIN}_{device_id}_lock"
        self._attr_name = "Lock"
        self._attr_icon = "mdi:lock-outline"

        # Link to the same device
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, device_id)})

    async def async_press(self) -> None:
        """Triggered when the button is pressed.

        Sends a request to lock the device.
        """

        try:
            await self.coordinator.hub.lock_device(self.device_id)
            _LOGGER.info("Sent lock command to device %s", self.device_id)
        except Exception as error:
            _LOGGER.error(
                "Failed to send lock command to %s: %s", self.device_id, error
            )
            raise
