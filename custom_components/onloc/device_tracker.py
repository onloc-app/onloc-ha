import logging
from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.helpers.device_registry import DeviceInfo
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

    def _fetchDevice(self):
        return self.coordinator.devices[self.device_id]

    def _fetchLocation(self):
        return self._fetchDevice().get("latest_location", {})

    @property
    def icon(self) -> str:
        return f"mdi:{self._fetchDevice().get('icon')}"

    @property
    def latitude(self) -> float | None:
        return self._fetchLocation().get("latitude")

    @property
    def longitude(self) -> float | None:
        return self._fetchLocation().get("longitude")

    @property
    def location_accuracy(self) -> int | None:
        accuracy = self._fetchLocation().get("accuracy")
        return int(accuracy) if accuracy is not None else 0

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        attributes: dict[str, Any] = {}

        location = self._fetchLocation()

        if (battery := location.get("battery")) is not None:
            attributes["battery"] = battery

        if (altitude := location.get("altitude")) is not None:
            attributes["altitude"] = altitude

        if (altitude_accuracy := location.get("altitude_accuracy")) is not None:
            attributes["altitude_accuracy"] = altitude_accuracy

        if (created_at := location.get("created_at")) is not None:
            attributes["last_seen"] = created_at

        if (icon := self._fetchDevice().get("icon")) is not None:
            attributes["icon"] = icon

        return attributes
