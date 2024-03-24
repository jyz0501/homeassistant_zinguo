"""
Zinguo platform for sensors
"""
import asyncio
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)
from homeassistant.util import slugify
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from custom_components.zinguo.const import *

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_TEMPERATURE): cv.string,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the ZiGate sensors."""
    devices = []
    for devType, name in config.items():
        if devType == CONF_TEMPERATURE:
            devices.append(ZinguoSensor(hass, name, devType))

    async_add_entities(devices)

class ZinguoSensor(SensorEntity):
    def __init__(self, hass, name, devType):
        """Initialize the sensor."""
        self.entity_id = f"sensor.{slugify(name)}"
        self._name = name
        self._type = devType
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_class(self):
        """Return the device class of this entity."""
        return DEVICE_CLASS_TEMPERATURE

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        async_dispatcher_connect(self.hass, CONF_EVENT_ZINGUO_SENSOR, self._handle_event)

    async def _handle_event(self, event):
        """Handle incoming events."""
        eventMsg = event.data
        if self._type in eventMsg:
            self._state = eventMsg[self._type]
            self.async_write_ha_state()

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return TEMP_CELSIUS
