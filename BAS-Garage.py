#!/usr/bin/env python

import udi_interface
import sys

LOGGER = udi_interface.LOGGER

from nodes import BasGarageController

if __name__ == "__main__":
    try:
        
        polyglot = udi_interface.Interface([BasGarageController])
        
        polyglot.start()

        control = BasGarageController(polyglot, 'controller', 'controller', 'PythonTemplate')

        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        LOGGER.warning("Received interrupt or exit...")
        
        polyglot.stop()
    except Exception as err:
        LOGGER.error('Exception: {0}'.format(err), exc_info=True)
    sys.exit(0)
