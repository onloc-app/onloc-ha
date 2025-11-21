import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_API_KEY, CONF_HOST, DOMAIN
from .coordinator import OnlocCoordinator
from .hub import CannotConnect, InvalidAuth, OnlocHub

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.DEVICE_TRACKER, Platform.SENSOR, Platform.BUTTON]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Onloc as config entry."""

    hub = OnlocHub(entry.data[CONF_HOST], entry.data[CONF_API_KEY])
    try:
        await hub.get_devices()
    except InvalidAuth:
        _LOGGER.error("Invalid API key")
        return False
    except CannotConnect:
        _LOGGER.error("Cannot reach Onloc")
        return False

    coord = OnlocCoordinator(hass, hub)
    await coord.async_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coord

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove Onloc."""

    coord = hass.data[DOMAIN].pop(entry.entry_id)
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await coord.hub.close()
    return ok
