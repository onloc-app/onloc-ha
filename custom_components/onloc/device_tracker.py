import logging
from typing import Any

from homeassistant.components.device_tracker import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
):
    coord = hass.data[DOMAIN][entry.entry_id]
    await coord.async_refresh()

    entities = []
    for dev_id, dev in coord.devices.items():
        entities.append(DeviceEntity(coord, dev_id, dev))
        entities.append(BatterySensor(coord, dev_id, dev))

    async_add_entities(entities, True)


class DeviceEntity(CoordinatorEntity, TrackerEntity):
    _attr_has_entity_name: bool = True
    _attr_source_type: SourceType = SourceType.GPS

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

    @property
    def icon(self) -> str:
        return f"mdi:{self.device.get('icon')}"

    @property
    def latitude(self) -> float | None:
        loc = self.coordinator.devices[self.device_id].get("latest_location", {})
        return loc.get("latitude")

    @property
    def longitude(self) -> float | None:
        loc = self.coordinator.devices[self.device_id].get("latest_location", {})
        return loc.get("longitude")

    @property
    def location_accuracy(self) -> int:
        loc = self.coordinator.devices[self.device_id].get("latest_location", {})
        return int(loc.get("accuracy", 0))

    @property
    def battery_level(self) -> int | None:
        loc = self.coordinator.devices[self.device_id].get("latest_location", {})
        return loc.get("battery")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        loc = self.coordinator.devices[self.device_id].get("latest_location", {})
        return {
            "altitude": loc.get("altitude"),
            "altitude_accuracy": loc.get("altitude_accuracy"),
            "last_seen": loc.get("created_at"),
            "icon": self.coordinator.devices[self.device_id].get("icon"),
        }


class BatterySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_entity_category = None

    def __init__(self, coord, device_id: str, device: dict):
        super().__init__(coord)
        self.device_id = device_id
        self.device = device

        self._attr_unique_id = f"{DOMAIN}_{device_id}_battery"
        self._attr_name = "Battery"
        self._attr_icon = "mdi:battery"

        # Link to the same device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
        )

    @property
    def native_value(self) -> int | None:
        loc = self.coordinator.devices[self.device_id].get("latest_location", {})
        return loc.get("battery")

    @property
    def icon(self) -> str:
        level = self.native_value
        if level is None:
            return "mdi:battery-unknown"
        elif level < 10:
            return "mdi:battery-alert"
        else:
            return f"mdi:battery-{((level + 5) // 10) * 10}"
