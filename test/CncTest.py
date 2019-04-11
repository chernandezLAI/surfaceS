import unittest

import sys
import time
import logging as log
import numpy as np
import matplotlib.pyplot as plt

if sys.platform.startswith('win32'):
    sys.path.append("C:\\Users\\jjayet\\Desktop\\SEM-PROJ_CNC_scanning\\surfaceS")
elif sys.platform.startswith('linux'):
    sys.path.append("~/EPFL/Cours/MA2/SEM-PROJ_CNC_scanning/surfaceS")
    log.debug("linux system")


from surfaceS import cnc

class TestCnc(unittest.TestCase):
    """
    Our basic test class
    """

    def test_simple_homing(self):
        c = cnc.Cnc()
        c.connect("COM5")
        c.start()
        c.home()
        time.sleep(20)
        c.sendStatusQuery()
        c.stop()

if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    unittest.main()
