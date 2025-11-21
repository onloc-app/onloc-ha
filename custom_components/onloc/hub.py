import logging
from typing import Any

import aiohttp
from aiohttp.client import ClientTimeout

from homeassistant.exceptions import HomeAssistantError

_LOGGER = logging.getLogger(__name__)


class CannotConnect(HomeAssistantError):
    pass


class InvalidAuth(HomeAssistantError):
    pass


class OnlocHub:
    def __init__(self, host: str, api_key: str):
        self.host = host.rstrip("/")
        self.api_key = api_key
        self._session: aiohttp.ClientSession | None = None

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
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
        ) as r:
            if r.status in (401, 403):
                raise InvalidAuth
            if r.status >= 400:
                raise CannotConnect
            return await r.json()

    async def get_devices(self) -> list[dict]:
        return await self._req("/api/devices")

    async def ring_device(self, device_id) -> None:
        url = f"{self.host}/api/devices/{device_id}/ring"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        async with self.session.post(
            url, headers=headers, timeout=ClientTimeout(total=15)
        ) as r:
            if r.status in (401, 403):
                raise InvalidAuth
            if r.status >= 400:
                raise CannotConnect
            return
