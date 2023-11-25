
import udi_interface
import sys
import time
import urllib3
import asyncio
from bascontrolns import Device, Platform

LOGGER = udi_interface.LOGGER

class BasGarageNode(udi_interface.Node):
    def __init__(self, polyglot, primary, address, name, door_ip, bc):
        super(BasGarageNode, self).__init__(polyglot, primary, address, name)
        self.poly = polyglot
        self.lpfx = '%s:%s' % (address,name)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        self.door_ip = door_ip
        self.bc = bc

    def start(self):
        if self.door_ip is not None:
            self.bc = Device(self.door_ip)

        ### Do we have a BASpi or an Edge Device ###
        if self.bc.ePlatform == Platform.BASC_PI or self.bc.ePlatform == Platform.BASC_PO: ### BASpi-6u6r Device is found
            LOGGER.info('connected to BASpi-6U6R')
        elif self.bc.ePlatform == Platform.BASC_ED: ### BASpi-Edge Device is found
            LOGGER.info('connected to BASpi-Edge')
            #self.setDriver('ST', 1)    
        elif self.bc.ePlatform == Platform.BASC_NONE: ### NO Device found
            LOGGER.info('Unable to connect to Device')
            LOGGER.info(self.door_ip)
        elif self.bc.ePlatform == Platform.BASC_PI or self.bc.ePlatform == Platform.BASC_PO or self.bc.ePlatform == Platform.BASC_ED:
            self.setDriver('ST', 1)
            LOGGER.debug('%s: get ST=%s',self.lpfx,self.getDriver('ST'))
        else:
            self.setDriver("ST", 0)
        
        # How many nodes or points does the device have
        LOGGER.info('\t' + str(self.bc.uiQty) + ' Universal inputs in this Device')
        LOGGER.info('\t' + str(self.bc.boQty) + ' Binary outputs in this Device')
        LOGGER.info('\t' + str(self.bc.vtQty) + ' Virtual points In This Device')

        # What are the Physical nodes or Device point currently reading
        LOGGER.info('Inputs')
        for i in range(1,7):
            LOGGER.info(str(self.bc.universalInput(i)))
        LOGGER.info('Outputs')
        for i in range(1,7):
            LOGGER.info(str(self.bc.binaryOutput(i)))

        ### Universal Inputs
        self.setInputDriver('GV0', 1)
        self.setInputDriver('GV1', 2)
        self.setInputDriver('GV2', 3)
        self.setInputDriver('GV3', 4)
        self.setInputDriver('GV4', 5)
        self.setInputDriver('GV5', 6)

        # Binary/Digital Outputs
        output_one = (self.bc.binaryOutput(1))
        output_two = (self.bc.binaryOutput(2))
        output_tre = (self.bc.binaryOutput(3))
        output_for = (self.bc.binaryOutput(4))
        output_fiv = (self.bc.binaryOutput(5))
        output_six = (self.bc.binaryOutput(6))

        # Binary/Digital Outputs
        self.setDriver('GV6', output_one, True, True)
        self.setDriver('GV7', output_two, True, True)
        self.setDriver('GV8', output_tre, True, True)
        self.setDriver('GV9', output_for, True, True)
        self.setDriver('GV10', output_fiv, True, True)
        self.setDriver('GV11', output_six, True, True)
    
    ### Universal Inputs Conversion ###
    def setInputDriver(self, driver, input):
        input_val = self.bc.universalInput(input)
        count = 0
        if input_val is not None:
            count = int(float(input_val))//1000
            self.setDriver(driver, count, True, True)
        else:
            pass        

    def poll(self, polltype):
        if 'longPoll' in polltype:
            LOGGER.debug('longPoll (node)')
        else:
            self.start()
            LOGGER.debug('shortPoll (node)')
        
    # Input Output Control       
        self.mapping = {
            'BON1' : {'input':'GV6', 'output':'GV0', 'index': (1)}, 
            'BON2' : {'input':'GV7', 'output':'GV1', 'index': (2)}, 
            'BON3' : {'input':'GV8', 'output':'GV2', 'index': (3)}, 
            'BON4' : {'input':'GV9', 'output':'GV3', 'index': (4)}, 
            'BON5' : {'input':'GV10', 'output':'GV4', 'index': (5)}, 
            'BON6' : {'input':'GV11', 'output':'GV5', 'index': (6)},
            'BOB1' : {'input':'GV6', 'output':'GV0', 'index': (1)}, 
            'BOB2' : {'input':'GV7', 'output':'GV1', 'index': (2)}, 
            'BOB3' : {'input':'GV8', 'output':'GV2', 'index': (3)}, 
            'BOB4' : {'input':'GV9', 'output':'GV3', 'index': (4)}, 
            'BOB5' : {'input':'GV10', 'output':'GV4', 'index': (5)}, 
            'BOB6' : {'input':'GV11', 'output':'GV5', 'index': (6)},
            }     

    # Delays status for door travel, stops theard 
    def setOn(self, command):
        #command = {'address': 'baspidoor1_id', 'cmd': 'BON1', 'query': {}}
        input = self.mapping[command['cmd']]['input']
        output = self.mapping[command['cmd']]['output']
        index = self.mapping[command['cmd']]['index']
        if self.bc.binaryOutput(index) == 0:
            self.bc.binaryOutput(index, 1)
            self.setDriver(input, 1)
            self.setDriver(output, 255)
            LOGGER.info('Output {} On'.format(index))
            time.sleep(1)
        if self.bc.binaryOutput(index) != 0:
            self.bc.binaryOutput(index, 0)
            self.setDriver(input, 0)
            self.setDriver(output, 255)
            LOGGER.info('Output {} Off'.format(index))
            LOGGER.info('Door Operating')
            time.sleep(15)
            self.start()

    # Used to show STOPPED status with no time delay between commands so you can position door or stop it anywhere 
    # Shows status of STOPPED if door has traveled full stroke then it will show open or close on refresh
    def setOn1(self, command):
        input = self.mapping[command['cmd']]['input']
        output = self.mapping[command['cmd']]['output']
        index = self.mapping[command['cmd']]['index']
        if self.bc.binaryOutput(index) == 0:
            self.bc.binaryOutput(index, 1)
            self.setDriver(input, 1)
            self.setDriver(output, 255)
            LOGGER.info('Output {} On'.format(index))
            time.sleep(1)
        if self.bc.binaryOutput(index) != 0:
            self.bc.binaryOutput(index, 0)
            self.setDriver(input, 0)
            self.setDriver(output, 0)
            LOGGER.info('Output {} Off'.format(index))
            LOGGER.info('Door Operating')

    def query(self,command=None):
        self.start()
        LOGGER.info(self.door_ip)
        LOGGER.info(self.bc)

    drivers = [
        {'driver': 'ST', 'value': 0, 'uom': 2},
        {'driver': 'GV0', 'value': 1, 'uom': 25},
        {'driver': 'GV1', 'value': 1, 'uom': 25},
        {'driver': 'GV2', 'value': 1, 'uom': 25},
        {'driver': 'GV3', 'value': 1, 'uom': 25},
        {'driver': 'GV4', 'value': 1, 'uom': 25},
        {'driver': 'GV5', 'value': 1, 'uom': 25},
        {'driver': 'GV6', 'value': None, 'uom': 80},
        {'driver': 'GV7', 'value': None, 'uom': 80},
        {'driver': 'GV8', 'value': None, 'uom': 80},
        {'driver': 'GV9', 'value': None, 'uom': 80},
        {'driver': 'GV10', 'value': None, 'uom': 80},
        {'driver': 'GV11', 'value': None, 'uom': 80},
        ]

    id = 'baspidoor1_id'

    commands = {
                    'BON1': setOn,
                    'BON2': setOn,
                    'BON3': setOn,
                    'BON4': setOn,
                    'BON5': setOn,
                    'BON6': setOn,
                    'BOB1': setOn1,
                    'BOB2': setOn1,
                    'BOB3': setOn1,
                    'BOB4': setOn1,
                    'BOB5': setOn1,
                    'BOB6': setOn1,
                    'PING': query
                }
    