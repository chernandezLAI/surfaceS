import unittest

import sys
import time
import numpy as np
import matplotlib.pyplot as plt
import logging as log

if sys.platform.startswith('win32'):
    sys.path.append("C:\\Users\\jjayet\\Desktop\\SEM-PROJ_CNC_scanning\\surfaceS")
elif sys.platform.startswith('linux'):
    sys.path.append("~/EPFL/Cours/MA2/SEM-PROJ_CNC_scanning/surfaceS")
    log.debug("linux system")


from surfaceS import SignalGenerator as SG

class TestSignalGenerator(unittest.TestCase):
    """
    Our basic test class
    """

    def test_connect(self):
        signalG = SG.SignalGenerator()
        signalG.connect(port="COM6")
        signalG.disconnect()

    def test_simple_setup(self):
        signalG = SG.SignalGenerator()
        signalG.connect(port="COM6")
        signalG.setChannel(channel=2)
        signalG.setFrequency(frequency=100)
        signalG.setOutput(state=True)
        time.sleep(5)
        signalG.setOutput(state=False)
        signalG.disconnect()

    def test_sine_setup(self):
        signalG = SG.SignalGenerator()
        signalG.connect(port="COM6")
        signalG.setChannel(channel=1)
        signalG.setFrequency(frequency=440)
        signalG.setWave("SINE", 3)
        signalG.setOutput(state=True)
        time.sleep(5)
        signalG.setOutput(state=False)
        signalG.disconnect()

    def test_send_data_ARB3(self):
        size = 1024
        data = np.zeros(size, dtype=np.uint16)

        for i in range(0, size-1):
            data[i] = 0.03*np.square(i)+0.01*i+1

        signalG = SG.SignalGenerator()
        signalG.connect(port="COM6")
        signalG.setChannel(channel=1)
        signalG.setWave("ARB", 3)
        signalG.setFrequency(frequency=440)

        signalG.setArbitraryWaveform(data, register=3, name="TEST_SQUARE3")

        signalG.setOutput(state=True)

        plt.plot(data)
        plt.show()

        #       time.sleep(30)
        signalG.setOutput(state=False)
        signalG.disconnect()

        time.sleep(3)

    def test_burst_mode(self):
        signalG = SG.SignalGenerator()
        signalG.connect(port="COM6")
        signalG.setChannel(channel=1)
        signalG.setFrequency(frequency=440)
        signalG.setWave("ARB", 3)
        signalG.setBurstMode()
        signalG.setOutput(state=True)
        time.sleep(2)
        for i in range(0,5):
            signalG.burst()
            time.sleep(1)
        signalG.setOutput(state=False)
        signalG.disconnect()

if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    unittest.main()
