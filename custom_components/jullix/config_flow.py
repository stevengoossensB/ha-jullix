from homeassistant import config_entries
import voluptuous as vol

from .const import DEFAULT_HOST, DOMAIN


class JullixConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="Jullix", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional("host", default=DEFAULT_HOST): str,
                }
            ),
            errors=errors,
        )
