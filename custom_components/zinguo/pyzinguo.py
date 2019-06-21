# _*_ coding: utf-8 _*_

import codecs
import logging
import requests
import hashlib
import json
import sys
from requests import Response
from custom_components.zinguo.const import *
from homeassistant.const import (CONF_NAME, CONF_MAC, CONF_TOKEN, CONF_USERNAME)

############################################################################################

############################################################################################
_LOGGER = logging.getLogger(__name__)


class ZinguoSwitchB2():

    def __init__(self, masterUser, password):
        self.password = password
        self.mac = None
        self.token = None
        self.masterUser = masterUser

        self.warmingSwitch1StateChange = False
        self.warmingSwitch2StateChange = False
        self.windSwitchStateChange = False
        self.lightSwitchStateChange = False
        self.ventilationSwitchStateChange = False

        self.warmingSwitch1StateOld = CONF_OFF
        self.warmingSwitch2StateOld = CONF_OFF
        self.windSwitchStateOld = CONF_OFF
        self.lightSwitchStateOld = CONF_OFF
        self.ventilationSwitchStateOld = CONF_OFF

        self.warmingSwitch1StateNew = CONF_OFF
        self.warmingSwitch2StateNew = CONF_OFF
        self.windSwitchStateNew = CONF_OFF
        self.lightSwitchStateNew = CONF_OFF
        self.ventilationSwitchStateNew = CONF_OFF

        self.temperatureState = '0'

        self.login()


    def login(self):
        url = 'http://114.55.66.106:8002/api/v1/customer/login'
        headers = {'User-Agent': 'okhttp/3.6.0',
                'Content-Type': 'text/plain;charset=UTF-8',
                'x-access-token': 'z-mYA09hZzegEq8FwSqL0LlRTB6SZyCvVthZJO05iX7biPWQxNSsBEOTbd0OGFI3'
                }
        sha1 = hashlib.sha1()
        sha1.update(self.password.encode('utf-8'))
        hash_pass = sha1.hexdigest()
        data = {'account': self.masterUser, 'password': hash_pass}

        try:
            r= requests.post(url, json=data, headers=headers, timeout = 2)
        except Exception as e:
            _LOGGER.debug('ZINGUO : login Exception')
            _LOGGER.debug('ZINGUO : except'+str(e))
            return False

        json_data = r.json()
        self.token = json_data['token']
        self.mac = json_data['deviceIds'][0]['mac']

        return True

    def get_status(self):
        _LOGGER.debug('ZINGUO : get_status')

        try:
            url="http://114.55.66.106:8002/api/v1/device/getDeviceByMac?mac=" + self.mac
            headers = {'User-Agent': 'okhttp/3.6.0',
                     'Content-Type': 'aplication/json;charset=UTF-8',
                   'x-access-token': self.token
                    }
            r = requests.get(url,headers=headers, timeout = 2)
        except Exception as e:
            _LOGGER.debug('ZINGUO : get_status Exception')
            _LOGGER.debug('ZINGUO : '+str(e))
            return False


        json_data = r.json()

        try:
            self.warmingSwitch1StateOld = self.warmingSwitch1StateNew
            self.warmingSwitch2StateOld = self.warmingSwitch2StateNew
            self.windSwitchStateOld = self.windSwitchStateNew
            self.lightSwitchStateOld = self.lightSwitchStateNew
            self.ventilationSwitchStateOld = self.ventilationSwitchStateNew

            self.warmingSwitch1StateNew = json_data[CONF_WARMING_SWITCH_1] #暖风一档
            self.warmingSwitch2StateNew = json_data[CONF_WARMING_SWITCH_2] #暖风二档
            self.windSwitchStateNew = json_data[CONF_WIND_SWITCH] #吹风
            self.lightSwitchStateNew = json_data[CONF_LIGHT_SWITCH]  #照明
            self.ventilationSwitchStateNew = json_data[CONF_VENTILATION_SWITCH] #排气

            self.temperatureState = json_data[CONF_TEMPERATURE]#温度
            return True
        except Exception as e:
            _LOGGER.debug('ZINGUO : json data Exception')
            _LOGGER.debug('ZINGUO : json data '+str(e)+':'+str(json_data))
            return False

    def set_old_state(self,switchName):
        if switchName == CONF_LIGHT_SWITCH:
            if self.lightSwitchStateOld == CONF_ON:
                self.lightSwitchStateOld = CONF_OFF
            elif self.lightSwitchStateOld == CONF_OFF:
                self.lightSwitchStateOld = CONF_ON

        if switchName == CONF_WIND_SWITCH:
            if self.windSwitchStateOld == CONF_ON:
                self.windSwitchStateOld = CONF_OFF
            elif self.windSwitchStateOld == CONF_OFF:
                self.windSwitchStateOld = CONF_ON

        if switchName == CONF_VENTILATION_SWITCH:
            if self.ventilationSwitchStateOld == CONF_ON:
                self.ventilationSwitchStateOld = CONF_OFF
            elif self.ventilationSwitchStateOld == CONF_OFF:
                self.ventilationSwitchStateOld = CONF_ON

        if switchName == CONF_WARMING_SWITCH_1:
            if self.warmingSwitch1StateOld == CONF_ON:
                self.warmingSwitch1StateOld = CONF_OFF
            elif self.warmingSwitch1StateOld == CONF_OFF:
                self.warmingSwitch1StateOld = CONF_ON

        if switchName == CONF_WARMING_SWITCH_2:
            if self.warmingSwitch2StateOld == CONF_ON:
                self.warmingSwitch2StateOld = CONF_OFF
            elif self.warmingSwitch2StateOld == CONF_OFF:
                self.warmingSwitch2StateOld = CONF_ON




    def get_state_change(self):
        if self.warmingSwitch1StateOld == self.warmingSwitch1StateNew:
            self.warmingSwitch1StateChange = False
        else:
            self.warmingSwitch1StateChange = True

        if self.warmingSwitch2StateOld == self.warmingSwitch2StateNew:
            self.warmingSwitch2StateChange = False
        else:
            self.warmingSwitch2StateChange = True

        if self.windSwitchStateOld == self.windSwitchStateNew:
            self.windSwitchStateChange = False
        else:
            self.windSwitchStateChange = True

        if self.lightSwitchStateOld == self.lightSwitchStateNew:
            self.lightSwitchStateChange = False
        else:
            self.lightSwitchStateChange = True

        if self.ventilationSwitchStateOld == self.ventilationSwitchStateNew:
            self.ventilationSwitchStateChange = False
        else:
            self.ventilationSwitchStateChange = True

    def toggle_zinguo_switch(self, switchName):
        url = "http://114.55.66.106:8002/api/v1/wifiyuba/yuBaControl"
        headers = {'User-Agent': 'okhttp/3.6.0' ,
                  'Content-Type':'aplication/json;charset=UTF-8',
                  'x-access-token':self.token
                  }
        data = {"mac":self.mac,
                switchName:1,
                "turnOffAll":0,
                "setParamter":False,
                "action":False,
                "masterUser":self.masterUser}

        try:
            r = requests.put(url, json=data, headers=headers, timeout = 2)
        except Exception as e:
            _LOGGER.debug('ZINGUO toggle_zinguo_switch Exception')
            _LOGGER.debug('ZINGUO toggle_zinguo_switch'+str(e))
            return False


        json_data = r.json()
        try:
            result = json_data['result']
            if result != "设置成功":
                self.set_old_state(switchName)
                return True
        except Exception as e:
            _LOGGER.debug('ZINGUO toggle_zinguo_switch return:'+str(e))
            return False

############################################################################################
