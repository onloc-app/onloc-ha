import logging
from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    await coord.async_refresh()

    entities = [
        DeviceEntity(coord, dev_id, dev) for dev_id, dev in coord.devices.items()
    ]
    async_add_entities(entities, True)


class DeviceEntity(CoordinatorEntity, TrackerEntity):
    _attr_has_entity_name = True
    _attr_source_type = SourceType.GPS

    _attr_device_info: DeviceInfo | None = None

    def __init__(self, coord, device_id: str, device: dict):
        super().__init__(coord)
        self.device_id = device_id
        self.device = device
        self._attr_unique_id = f"{DOMAIN}_{device_id}"
        self._attr_name = "Location"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            name=device.get("name"),
        )

        self._data = self.coordinator.devices[self.device_id].get("latest_location", {})

    @property
    def icon(self) -> str:
        return f"mdi:{self.device.get('icon')}"

    @property
    def latitude(self) -> float | None:
        return self._data.get("latitude")

    @property
    def longitude(self) -> float | None:
        return self._data.get("longitude")

    @property
    def location_accuracy(self) -> int | None:
        return int(self._data.get("accuracy", 0))

    @property
    def battery_level(self) -> int | None:
        return self._data.get("battery")

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        return {
            "altitude": self._data.get("altitude"),
            "altitude_accuracy": self._data.get("altitude_accuracy"),
            "last_seen": self._data.get("created_at"),
            "icon": self.coordinator.devices[self.device_id].get("icon"),
        }
