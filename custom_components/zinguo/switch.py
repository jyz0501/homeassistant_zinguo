"""
Zinguo platform for switches
"""
import json
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.const import CONF_NAME, CONF_MAC, CONF_TOKEN, CONF_USERNAME, ATTR_NAME
from custom_components.zinguo.const import *

_LOGGER = logging.getLogger(__name__)

deviceType = [
    CONF_WARMING_SWITCH_1,
    CONF_WARMING_SWITCH_2,
    CONF_WIND_SWITCH,
    CONF_LIGHT_SWITCH,
    CONF_VENTILATION_SWITCH,
]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(devType): cv.string for devType in deviceType
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the ZiGate switches."""
    devices = []
    for devType, name in config.items():
        devices.append(ZinguoSwitch(hass, name, devType))

    async_add_entities(devices)

class ZinguoSwitch(SwitchEntity):
    def __init__(self, hass, name, devType):
        """Initialize the switch."""
        self.entity_id = f"switch.{slugify(name)}"
        self._name = name
        self._type = devType
        self._state = False
        self._hass = hass

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        await self._call_toggle_service(True)


    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        await self._call_toggle_service(False)

    async def _call_toggle_service(self, turn_on):
        """Call toggle service."""
        service_data = {"name": self._type}
        if turn_on:
            service = SERVICE_TOGGLE_ZINGUO_SWITCH
        else:
            service = SERVICE_TOGGLE_ZINGUO_SWITCH

        await self._hass.services.async_call(DOMAIN, service, service_data)

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        async_dispatcher_connect(self._hass, CONF_EVENT_ZINGUO_STATE_CHANGE, self._handle_event)

    async def _handle_event(self, event):
        """Handle incoming events."""
        eventMsg = event.data
        if self._type in eventMsg:
            if eventMsg[self._type] == CONF_ON:
                self._state = True
            elif eventMsg[self._type] == CONF_OFF:
                self._state = False
            self.async_write_ha_state()
