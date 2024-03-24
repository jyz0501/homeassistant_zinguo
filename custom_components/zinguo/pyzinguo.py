"""
峥果智能设备控制组件
"""
import logging
import hashlib
import json
import requests
from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_MAC,
)
from homeassistant.helpers.entity import ToggleEntity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "zinguo"

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Zinguo platform."""
    username = config[DOMAIN][CONF_USERNAME]
    password = config[DOMAIN][CONF_PASSWORD]
    mac_address = config[DOMAIN][CONF_MAC]

    zinguo_switch = ZinguoSwitch(username, password, mac_address)

    add_entities([zinguo_switch])

class ZinguoSwitch(ToggleEntity):
    """Representation of a Zinguo switch."""

    def __init__(self, username, password, mac_address):
        """Initialize the switch."""
        self._username = username
        self._password = password
        self._mac_address = mac_address
        self._state = None

    @property
    def name(self):
        """Return the name of the switch."""
        return "Zinguo Switch"

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state == "on"

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._set_switch_state("on")

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._set_switch_state("off")

    def _set_switch_state(self, state):
        """Update the switch state."""
        url = "http://iot.zinguo.com/api/v1/wifiyuba/yuBaControl"
        headers = {
            "User-Agent": "CFNetwork/1494.0.7 Darwin/23.4.0",
            "Content-Type": "application/json;charset=UTF-8",
        }
        sha1 = hashlib.sha1()
        sha1.update(self._password.encode("utf-8"))
        hash_pass = sha1.hexdigest()
        data = {
            "mac": self._mac_address,
            "switchName": 1 if state == "on" else 0,
            "turnOffAll": 0,
            "setParamter": False,
            "action": False,
            "masterUser": self._username,
        }

        try:
            response = requests.put(url, json=data, headers=headers, timeout=2)
            response.raise_for_status()
            result = response.json().get("result")
            if result == "设置成功":
                self._state = state
            else:
                _LOGGER.error("Failed to set switch state")
        except requests.exceptions.RequestException as ex:
            _LOGGER.error("Error communicating with Zinguo API: %s", ex)
