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


from surfaceS import Oscilloscope as Osc

class TestOscilloscope(unittest.TestCase):
    """
    Our basic test class
    """

    def test_connect(self):
        log.basicConfig(level=log.DEBUG)
        osc = Osc.Oscilloscope()
        osc.connect()
        osc.printID()
        osc.disconnect()

    def test_acquire(self):
        log.basicConfig(level=log.DEBUG)
        osc = Osc.Oscilloscope()
        osc.connect()
        osc.setGrid()
        osc.setTrigger(triggerLevel=0.75)
        data = osc.acquire()
        time.sleep(5)
        plt.subplot(1,2,1)
        plt.plot(data["data"])
        fftData = np.fft.fft(data["data"])
        plt.subplot(1,2,2)
        plt.plot(fftData)
        plt.show()
        osc.disconnect()

    def test_acquire_oscillo_minh(self):
        log.basicConfig(level=log.DEBUG)
        osc = Osc.Oscilloscope()
        osc.connect()
        osc.setGrid(timeDivision=0.0001,voltDivision=0.2,channel=1,unitVoltDivision="V",unitTimeDivision="S")
        osc.setTrigger(triggerLevel=-10.2)
        data = osc.acquire(forceAcquisition=True)
        time.sleep(5)
        plt.subplot(1,2,1)
        plt.plot(data["data"])
        fftData = np.fft.fft(data["data"])
        plt.subplot(1,2,2)
        plt.plot(fftData)
        plt.show()
        osc.disconnect()

if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    unittest.main()
