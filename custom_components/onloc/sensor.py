import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.sensor.const import SensorStateClass
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    coord = hass.data[DOMAIN][entry.entry_id]
    await coord.async_refresh()

    entities = [
        BatterySensor(coord, dev_id, dev) for dev_id, dev in coord.devices.items()
    ]
    async_add_entities(entities, True)


class BatterySensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.MEASUREMENT

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
        if level < 10:
            return "mdi:battery-outline"
        if level == 100:
            return "mdi:battery"
        return f"mdi:battery-{int(level / 10)}0"
