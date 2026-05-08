"""Data update coordinator for the Onloc integration."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .hub import OnlocHub

_LOGGER = logging.getLogger(__name__)


class OnlocCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Manages data fetching."""

    def __init__(self, hass: HomeAssistant, hub: OnlocHub) -> None:
        """Initializes the integration."""

        self.hub = hub
        self.devices: dict[str, dict[str, Any]] = {}

        super().__init__(
            hass,
            _LOGGER,
            name="Onloc",
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data from the API."""

        raw = await self.hub.get_devices()

        self.devices = {}

        device_list = raw.get("devices", [])
        for device in device_list:
            device_id = device.get("id")

            if device_id:
                self.devices[str(device_id)] = device

        return self.devices
