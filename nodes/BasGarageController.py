

"""
Get the polyinterface objects we need. 
a different Python module which doesn't have the new LOG_HANDLER functionality
"""
import udi_interface
import time
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET
from enum import Enum
import ipaddress
import bascontrolns
from bascontrolns import Device, Platform

# My Template Node
from nodes import BasGarageNode

"""
Some shortcuts for udi interface components

- LOGGER: to create log entries
- Custom: to access the custom data class
- ISY:    to communicate directly with the ISY (not commonly used)
"""
LOGGER = udi_interface.LOGGER
LOG_HANDLER = udi_interface.LOG_HANDLER
Custom = udi_interface.Custom
ISY = udi_interface.ISY

# IF you want a different log format than the current default
LOG_HANDLER.set_log_format('%(asctime)s %(threadName)-10s %(name)-18s %(levelname)-8s %(module)s:%(funcName)s: %(message)s')

class BasGarageController(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name):
        super(BasGarageController, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.name = 'Door Controller'  # override what was passed in
        self.hb = 0
        self.logging = None


        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')

        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.LOGLEVEL, self.handleLevelChange)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.ready()
        self.poly.addNode(self)

    def start(self):
        self.poly.updateProfile()
        self.poly.setCustomParamsDoc()
        self.discover()
        
        def handleLevelChange(self, level):
            LOGGER.info('New log level: {}'.format(level))
    
    # Class form bascontrolns
    class bc:
        def __init__(self, sIpAddress, ePlatform):
            self.bc = Device()
            self.ePlatform = ePlatform

    def get_request(self, url):
        try:
            r = requests.get(url, auth=HTTPBasicAuth('http://' + self.door_ip + '/cgi-bin/xml-cgi')) 
            if r.status_code == requests.codes.ok:
                if self.debug_enable == 'True' or self.debug_enable == 'true':
                    print(r.content)

                return r.content
            else:
                LOGGER.error("BASpi6u6r.get_request:  " + r.content)
                return None

        except requests.exceptions.RequestException as e:
            LOGGER.error("Error: " + str(e))

    def discover(self, *args, **kwargs):
        if self.door_ip is not None:
            self.bc = Device(self.door_ip)
            self.poly.addNode(BasGarageNode(self.poly, self.address, 'baspidoor1_id', 'Doors 1-6', self.door_ip, self.bc))

    def delete(self):
        LOGGER.info('Deleted Garage Door Controller.')

    def stop(self):
        LOGGER.debug('NodeServer stopped.')

    def set_module_logs(self,level):
        logging.getLogger('urllib3').setLevel(level)

    def check_params(self):
        self.Notices.clear()
        default_door_ip = "127.0.0.1"
        
        self.door_ip = self.Parameters.door_ip
        if self.door_ip is None:
            self.door_ip = default_door_ip
            LOGGER.error('check_params: user not defined in customParams, please add it.  Using {}'.format(default_door_ip))
            self.door_ip = default_door_ip

        if self.door_ip == default_door_ip:
            self.Notices['auth'] = 'Please set proper ip address in configuration page'

    def parameterHandler(self, params):
        self.Parameters.load(params)
        LOGGER.debug('Loading parameters now')
        self.check_params()
    
    def handleLevelChange(self, level):
        LOGGER.info('New log level: {}'.format(level))

    def query(self,command=None):
        self.reportDrivers()
        nodes = self.poly.getNodes()
        for node in nodes:
            nodes[node].reportDrivers()

    def remove_notices_all(self,command):
        LOGGER.info('remove_notices_all: notices={}'.format(self.Notices))
        # Remove all existing notices
        self.Notices.clear()

    id = 'controller'
    commands = {
        'QUERY': query,
        'REMOVE_NOTICES_ALL': remove_notices_all,
        }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
    ]
