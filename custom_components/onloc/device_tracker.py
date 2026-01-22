import logging
from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Creates the device's tracker entity.

    This entity is the one shown on the map that
    stores the device's location.
    """

    coordinator = hass.data[DOMAIN][entry.entry_id]
    await coordinator.async_refresh()

    entities = [
        DeviceEntity(coordinator, device_id, device)
        for device_id, device in coordinator.devices.items()
    ]
    async_add_entities(entities, True)


class DeviceEntity(TrackerEntity):
    """The tracker entity."""

    _attr_has_entity_name = True
    _attr_source_type = SourceType.GPS

    def __init__(self, coordinator, device_id: str, device: dict):
        """Initializes the tracker."""

        super().__init__()
        self.coordinator = coordinator

        self.device_id = device_id
        self.device = device
        self._attr_unique_id = f"{DOMAIN}_{device_id}"
        self._attr_name = "Location"

    def _fetchDevice(self):
        return self.coordinator.devices[self.device_id]

    def _fetchLocation(self):
        return self._fetchDevice().get("latest_location", {})

    @property
    def device_info(self) -> DeviceInfo:
        """Information on the device."""

        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)}, name=self.device.get("name")
        )

    @property
    def icon(self) -> str:
        """The icon representing the device."""

        return f"mdi:{self._fetchDevice().get('icon')}"

    @property
    def latitude(self) -> float | None:
        """Device's latest latitude."""

        return self._fetchLocation().get("latitude")

    @property
    def longitude(self) -> float | None:
        """Device's latest longitude."""

        return self._fetchLocation().get("longitude")

    @property
    def location_accuracy(self) -> float:
        """Device's latest locations's accuracy."""

        accuracy = self._fetchLocation().get("accuracy")
        return float(accuracy) if accuracy is not None else 0

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Some extra information about the device's location."""

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
