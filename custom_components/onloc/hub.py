import logging
from socket import timeout
from typing import Any, TypedDict

import aiohttp
from aiohttp.client import ClientTimeout

from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)


class CannotConnect(HomeAssistantError):
    """Error for connection problems."""


class InvalidAuth(HomeAssistantError):
    """Error for invalid auth."""


class DevicesResponse(TypedDict):
    """Response type for devices."""

    devices: list[dict[str, Any]]


class OnlocHub:
    """Bridge between Home Assistant and Onloc.

    This class is responsible for fetching data directly
    from Onloc's API.
    """

    def __init__(self, host: str, api_key: str):
        """Initializes the hub."""

        self.host = host.rstrip("/")
        self.api_key = api_key
        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        """Returns a reusable aiohttp client session."""

        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        """Closes the aiohttp client session."""

        if self._session and not self._session.closed:
            await self._session.close()

    async def _req(self, endpoint: str) -> Any:
        url = f"{self.host}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        async with self.session.get(
            url, headers=headers, timeout=ClientTimeout(total=15)
        ) as response:
            if response.status in (401, 403):
                raise InvalidAuth
            if response.status >= 400:
                raise CannotConnect
            return await response.json()

    async def get_devices(self) -> DevicesResponse:
        """Fetches the devices from Onloc's API."""

        return await self._req("/api/devices")

    async def ring_device(self, device_id) -> None:
        """Sends a ring command to Onloc's API in order to ring a device."""

        url = f"{self.host}/api/devices/{device_id}/ring"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        async with self.session.post(
            url, headers=headers, timeout=ClientTimeout(total=15)
        ) as response:
            if response.status in (401, 403):
                raise InvalidAuth
            if response.status >= 400:
                raise CannotConnect
            return

    async def lock_device(self, device_id) -> None:
        """Sends a lock command to Onloc's API in order to lock a device."""

        url = f"{self.host}/api/devices/{device_id}/lock"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        async with self.session.post(
            url, headers=headers, timeout=ClientTimeout(total=15)
        ) as response:
            if response.status in (401, 403):
                raise InvalidAuth
            if response.status >= 400:
                raise CannotConnect
            return
