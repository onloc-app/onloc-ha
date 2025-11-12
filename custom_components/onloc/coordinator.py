import logging
from datetime import timedelta
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
        for dev in device_list:
            dev_id = dev.get("id")
            if dev_id:
                self.devices[str(dev_id)] = dev
        return self.devices
