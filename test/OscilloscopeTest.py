import unittest

import sys
import time
import logging as log

if sys.platform.startswith('win32'):
    sys.path.append("C:\\Users\\jjayet\\Desktop\\SEM-PROJ_CNC_scanning\\surfaceS")
elif sys.platform.startswith('linux'):
    sys.path.append("~/EPFL/Cours/MA2/SEM-PROJ_CNC_scanning/surfaceS")
    log.debug("linux system")


from src import Oscilloscope as Osc

class TestOscilloscope(unittest.TestCase):
    """
    Our basic test class
    """

    def test_connect(self):
        log.basicConfig(level=log.DEBUG)
        osc = Osc.Oscilloscope()
        osc.connect()
        osc.printID()
        #osc.acquire()
        #osc.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        osc.disconnect()

    def test_acquire(self):
        log.basicConfig(level=log.DEBUG)
        osc = Osc.Oscilloscope()
        osc.connect()
        osc.acquire()
        osc.disconnect()

    def test_buzzer(self):
        log.basicConfig(level=log.DEBUG)
        osc = Osc.Oscilloscope()
        osc.connect()
        print(osc.query("BUZZER"))
        osc.disconnect()

if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    unittest.main()
