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
=================================

*Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
*Last modification:* 24.05.2019

In this scenario, we measure the vibration on an array full of points.

"""

import threading
import time
import queue
import logging as log
import string
import serial

import pandas as pd

import Oscilloscope as Osc
import SignalGenerator as SG
import cnc as CNC

# CNC default parameters
CNC_PORT = "COM5"
START_X = -270.0
START_Y = -232.0
START_Z = -2.003

NB_POINT_X = 2
NB_POINT_Y = 2
STEP_X = 10.0
STEP_Y = 10.0

# Signal Generator default parameters
SG_PORT = "COM6"
WAVE_TYPE = "SINE"
FREQUENCY = 10000
CHANNEL_SG = 1

# Oscilloscope and acquisition default parameters
OSC_IP = "128.178.201.9"
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
    def __init__(self, cnc, osc, sg, params):
        self.experimentParameters = params
        self.signalGenerator = sg
        self.osc = osc
        self.cnc = cnc

        self.channelOnSG = self.experimentParameters['channel_sg']
        self.frequency = self.experimentParameters['frequency']
        self.waveType = self.experimentParameters['wave_type']
        self.nbPointX = self.experimentParameters['nb_point_x']
        self.nbPointY = self.experimentParameters['nb_point_y']
        self.startX = self.experimentParameters['start_x']
        self.startY = self.experimentParameters['start_y']

    def startScanning(self):
        # Configure signal generator
        self.signalGenerator.setChannel(self.channelOnSG)
        self.signalGenerator.setFrequency(self.frequency)
        self.signalGenerator.setWave(self.waveType, 1)
        self.signalGenerator.setBurstMode()

        self.osc.setGrid(self.experimentParameters['time_division'], \
                         self.experimentParameters['volt_division_reference'], \
                         self.experimentParameters['reference_channel'], \
                         self.experimentParameters['unit_volt_division'], \
                         self.experimentParameters['unit_time_division'])
        self.osc.setGrid(self.experimentParameters['time_division'], \
                         self.experimentParameters['volt_division_vibrometer'], \
                         self.experimentParameters['vibrometer_channel'], \
                         self.experimentParameters['unit_volt_division'], \
                         self.experimentParameters['unit_time_division'])
        self.osc.setTrigger(self.experimentParameters['trigger_level'], \
                            self.experimentParameters['trigger_delay'], \
                            self.experimentParameters['reference_channel'], \
                            self.experimentParameters['trigger_mode'], \
                            self.experimentParameters['unit_volt_division'])

        time.sleep(5)

        self.cnc.unlock()

        positionLock = threading.Event()

        ########################################################################
        # Make measurements
        ########################################################################

        measuring = True
        nbPoint = self.nbPointX * self.nbPointY

        xpoint = 0
        ypoint = 0
        xIncrement = 1

        data = pd.DataFrame()

        targetX = xpoint*self.experimentParameters['step_x'] + self.startX
        targetY = ypoint*self.experimentParameters['step_y'] + self.startY

        self.cnc.goTo(x=self.startX, y=self.startY, event=positionLock)

        self.signalGenerator.setOutput(state=True)

        while measuring:
            log.debug("Start signal and acquisition")
            #time.sleep(2)
            self.osc.setTrigger(self.experimentParameters['trigger_level'], \
                                self.experimentParameters['trigger_delay'], \
                                self.experimentParameters['reference_channel'], \
                                self.experimentParameters['trigger_mode'], \
                                self.experimentParameters['unit_volt_division'])
            log.debug("Waiting to be in position...")
            positionLock.wait()
            log.debug("In position !")
            positionLock.clear()
            time.sleep(self.experimentParameters['delay_before_measuring'])
            self.signalGenerator.burst()
            time.sleep(self.experimentParameters['time_division']*0.01) # Time in ms

            # Count the number of point measured
            xpoint += xIncrement
            if xpoint >= self.nbPointX or xpoint < 0 :
                xIncrement = -xIncrement
                xpoint += xIncrement
                ypoint +=1
                if ypoint > self.nbPointY:
                    measuring = False

            targetX = xpoint*self.experimentParameters['step_x'] + self.startX
            targetY = ypoint*self.experimentParameters['step_y'] + self.startY
            log.debug(f'Going to {targetX},{targetY}')
            self.cnc.goTo(x=targetX, y=targetY, event=positionLock)

            tmpData = self.osc.acquire(readOnly=True, channel=self.experimentParameters['vibrometer_channel'])
            data[f'{targetX},{targetY}'] = tmpData['data']

            log.info("Measure done !")

        self.signalGenerator.setOutput(state=False)

        #data.to_csv("data1.csv")
        return data
