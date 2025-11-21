from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .hub import OnlocHub

_LOGGER = logging.getLogger(__name__)


class OnlocCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, hub: OnlocHub):
        self.hub = hub
        self.devices = {}
        super().__init__(
            hass,
            _LOGGER,
            name="Onloc",
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self):
        raw = await self.hub.get_devices()

        self.devices = {}
        device_list = raw.get("devices", [])
        for device in device_list:
            device_id = device.get("id")
            if device_id:
                self.devices[str(device_id)] = device
        return self.devices
