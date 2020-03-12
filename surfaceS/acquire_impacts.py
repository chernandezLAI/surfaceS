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
The ``Acquire Impacts`` module
=================================

*Author:* [Camilo Hernandez](mailto:camilo.hernandez@epfl.ch)
*Last modification:* 26.11.2019

In this scenario, we acquire the flexural waves that porgapage in a surface after
an impact has occured, the vibrations are acquired at a single point or at an array
of points using piezoelectric patches.

Up to this moment maximum 3 signals can be acquired using an oscilloscope, future
developements need to be and will be done to acquire musing a DaQ.

"""

import threading
import time
import queue
import logging as log
import string
import serial

import pandas as pd

import Oscilloscope as Osc
import SignalGeneratorTCPIP as SG
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
SG_IP = "128.178.201.37"
SG_PORT = "9221"
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

class SurfaceImpactGenerator():
    """
    Class which handle the acquisition process.

    :param cnc: The handler which controls the CNC.
    :type cnc: CNC.Cnc
    :param osc: The handler which controls the oscilloscope.
    :type osc: Osc.Oscilloscope
    :param sg: The handler which controls the signal generator.
    :type sg: SG.SignalGeneratorTCPIP
    :param params: The experiment parameters
    :type params: dict

    """
    def __init__(self, cnc, osc, sg, params):
        self.experimentParameters = params
        self.signalGenerator = sg
        self.osc = osc
        self.cnc = cnc

        self.channelOnSG = self.experimentParameters['channel_sg']
        self.frequency = self.experimentParameters['frequency']
        self.waveType = self.experimentParameters['wave_type']
        self.pulseAmpVPPSG = self.experimentParameters['pulse_ampVPP_sg']
        self.pulseWidtSG = self.experimentParameters['pulse_width_sg']
        self.nbPointX = self.experimentParameters['nb_point_x']
        self.nbPointY = self.experimentParameters['nb_point_y']
        self.startX = self.experimentParameters['start_x']
        self.startY = self.experimentParameters['start_y']

    def startAcquiring(self):
        """
        Start the impact acquisition process.

        :return: A dataframe containing the acquisitions.
        :rtype: pd.Dataframe

        """
        # Configure signal generator
        self.signalGenerator.setChannel(self.channelOnSG)
        self.signalGenerator.setWave("PULSE")
        self.signalGenerator.setPulse(self.frequency, self.pulseAmpVPPSG/2, "VPP", self.pulseAmpVPPSG/4, self.pulseWidtSG)
        self.signalGenerator.setBurstMode(self.channelOnSG)
        self.signalGenerator.beep()

        # Configure oscilloscope
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
        # Make acquisition
        ########################################################################

        acquiring = True
        nbPoint = self.nbPointX * self.nbPointY

        xpoint = 0
        ypoint = 0
        xIncrement = 1
        actualSample = 1

        data = pd.DataFrame()

        targetX = xpoint*self.experimentParameters['step_x'] + self.startX
        targetY = ypoint*self.experimentParameters['step_y'] + self.startY

        self.cnc.goTo(x=self.startX, y=self.startY, event=positionLock)

        self.signalGenerator.setOutput(state=True)

        while acquiring:
            log.debug(f'Start signal and acquisition in position {targetX},{targetY}')
            #time.sleep(2)

            log.debug("Waiting to be in position...")
            positionLock.wait()
            log.debug("In position !")
            positionLock.clear()
            self.signalGenerator.burst() #IMPORTANT Forced Impact to lubrify the Pneumatic piston NOT RECORDED
            time.sleep(self.experimentParameters['delay_before_measuring']/2) # Wait half of the delay_before_measuring time
            while actualSample <= self.experimentParameters['samples_per_point']: # While Sample Number minor or equal to Number of samples per point
                time.sleep(self.experimentParameters['delay_before_measuring'])
                self.osc.setTrigger(self.experimentParameters['trigger_level'], \
                                    self.experimentParameters['trigger_delay'], \
                                    self.experimentParameters['reference_channel'], \
                                    self.experimentParameters['trigger_mode'], \
                                    self.experimentParameters['unit_volt_division'])

                self.signalGenerator.burst()
                time.sleep(self.experimentParameters['time_division']*0.01) # Time in ms
                tmpData = self.osc.acquire(readOnly=True, channel=self.experimentParameters['vibrometer_channel'])
                data[f'X{targetX}_Y{targetY}_S{actualSample}'] = tmpData['data']
                log.debug(f'Acquired Sample Number {actualSample} in position {targetX},{targetY}')
                #Save Data in a Temporal File
                data.to_pickle("dataTEMP.pkl")

                actualSample += 1 # Increment Sample number counter

            actualSample = 1 # Reset Sample number counter

            # Count the number of point acquired
            xpoint += xIncrement
            if xpoint >= self.nbPointX or xpoint < 0 :
                xIncrement = -xIncrement
                xpoint += xIncrement
                ypoint +=1
                if ypoint > self.nbPointY:
                    acquiring = False

            targetX = xpoint*self.experimentParameters['step_x'] + self.startX
            targetY = ypoint*self.experimentParameters['step_y'] + self.startY
            log.debug(f'Going to {targetX},{targetY}')
            self.cnc.goTo(x=targetX, y=targetY, event=positionLock)

            log.info("Acquisiton done !")

        self.signalGenerator.setOutput(state=False)

        return data
