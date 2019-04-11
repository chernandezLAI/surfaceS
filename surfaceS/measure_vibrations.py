################################################################################
 # MIT License
 #
 # Copyright (c) 2019 surfaceS
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documentation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in all
 # copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 # SOFTWARE.
 ################################################################################
"""
 The ``Measure vibrations`` module
 ======================

 *Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
 *Last modification:* 11.04.2019

 Scenario 1

 """

import threading
import time
import queue
import logging as log
import string
import serial

from surfaceS import Oscilloscope as Osc
from surfaceS import SignalGenerator as SG
from surfaceS import cnc as CNC

# CNC default parameters
CNC_PORT = "COM5"
START_X = -270.0
START_Y = -232.0
START_Z = -2.003

NB_POINT_X = 10
NB_POINT_Y = 10
STEP_X = 10.0
STEP_Y = 10.0

# Signal Generator default parameters
SG_PORT = "COM6"
WAVE_TYPE = "SINE"
FREQUENCY = 10000
CHANNEL_SG = 1

# Oscilloscope and acquisition default parameters
OSC_IP = "128.178.201.12"
VIBROMETER_CHANNEL = 2
REFERENCE_CHANNEL = 1
UNIT_TIME_DIVISION = "MS"
UNIT_VOLT_DIVISION = "MV"
VOLT_DIVISION_VIBROMETER = 20
VOLT_DIVISION_REFERENCE = 500
TIME_DIVISION = 5
TRIGGER_LEVEL = 0
TRIGGER_MODE = "SINGLE"
TRIGGER_DELAY = -20

log.basicConfig(level=log.DEBUG)

class SurfaceVibrationsScanner():
    def __init__(self):
        self.signalGenerator = SG.SignalGenerator()
        self.osc = Osc.Oscilloscope()
        self.cnc = CNC.Cnc()

        self.channelOnSG = CHANNEL_SG
        self.frequency = FREQUENCY
        self.waveType = WAVE_TYPE
        self.nbPointX = NB_POINT_X
        self.nbPointY = NB_POINT_Y
        self.startX = START_X
        self.startY = START_Y

    def startScanning(self):
        self.osc.connect(OSC_IP)
        self.signalGenerator.connect("COM6")
        self.cnc.connect("COM5")

        # Starting CNC controller (asynchronous call)
        self.cnc.start()

        # Configure signal generator
        self.signalGenerator.setChannel(self.channelOnSG)
        self.signalGenerator.setFrequency(self.frequency)
        self.signalGenerator.setWave(self.waveType, 1)
        self.signalGenerator.setBurstMode()

        # Home CNC (asynchronous call)
        self.cnc.home()

        # Configure Oscilloscope

        self.osc.setGrid(timeDivision=TIME_DIVISION,voltDivision=VOLT_DIVISION_REFERENCE,channel=REFERENCE_CHANNEL,unitVoltDivision=UNIT_VOLT_DIVISION,unitTimeDivision=UNIT_TIME_DIVISION)
        self.osc.setGrid(timeDivision=TIME_DIVISION,voltDivision=VOLT_DIVISION_VIBROMETER,channel=VIBROMETER_CHANNEL,unitVoltDivision=UNIT_VOLT_DIVISION,unitTimeDivision=UNIT_TIME_DIVISION)
        self.osc.setTrigger(triggerLevel=TRIGGER_LEVEL,triggerDelay=-20,channel=REFERENCE_CHANNEL,triggerMode=TRIGGER_MODE, unitTriggerLevel=UNIT_VOLT_DIVISION)

        time.sleep(5)

        #self.cnc.home()

        positionLock = threading.Event()

        ########################################################################
        # Make measurements
        ########################################################################

        measuring = True
        nbPoint = self.nbPointX * self.nbPointY

        xpoint = 1
        ypoint = 1

        while measuring:

            targetX = xpoint*STEP_X + self.startX
            targetY = ypoint*STEP_Y + self.startY

            log.debug(f'Going to {targetX},{targetY}')
            self.cnc.goTo(x=targetX, y=targetY, event=positionLock)

            log.debug("Waiting to be in position...")
            positionLock.wait()
            positionLock.clear()
            log.debug("Start signal and acquisition")
            self.signalGenerator.setOutput(state=True)
            time.sleep(2)
            self.osc.setTrigger(triggerLevel=TRIGGER_LEVEL,triggerDelay=-0.02,channel=REFERENCE_CHANNEL,triggerMode=TRIGGER_MODE, unitTriggerLevel=UNIT_VOLT_DIVISION)
            time.sleep(2)
            self.signalGenerator.burst()
            time.sleep(1)
            data = self.osc.acquire(readOnly=True)
            self.signalGenerator.setOutput(state=False)

            log.info("Measure done !")

            # Count the number of point measured
            xpoint += 1
            if xpoint > self.nbPointX :
                xpoint = 1
                ypoint +=1
                if ypoint > self.nbPointY:
                    measuring = False

        ########################################################################
        # Disconnect everything
        ########################################################################

        self.osc.disconnect()
        self.signalGenerator.disconnect()
        self.cnc.stop()
