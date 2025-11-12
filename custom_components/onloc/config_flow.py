import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_API_KEY
from .const import DOMAIN
from .hub import OnlocHub, CannotConnect, InvalidAuth

SCHEMA = vol.Schema({vol.Required(CONF_HOST): str, vol.Required(CONF_API_KEY): str})


class OnlocFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input:
            hub = OnlocHub(user_input[CONF_HOST], user_input[CONF_API_KEY])
            try:
                await hub.get_devices()
                await hub.close()
                return self.async_create_entry(title="Onloc", data=user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"
            finally:
                await hub.close()
        return self.async_show_form(step_id="user", data_schema=SCHEMA, errors=errors)
