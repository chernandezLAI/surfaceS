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
 The ``Oscilloscope`` module
 ===========================

 *Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
 *Last modification:* 09.05.2019

 This module is a class to handle an oscilloscope connected on the LAN.
 For now, it uses the VICP protocol based on pyvisa and the NI backend.

 Support
 -------

 + LeCroy Wavesurfer 3024.

 """

BAUD_RATE = 115200
PORT = 1861

import visa
from pyvisa.resources import MessageBasedResource

import logging as log
import string
import numpy as np

#log.basicConfig(level=log.DEBUG)

class Oscilloscope():
    def __init__(self, parent=None):
        self.nbrSamplesSeconde = 4000000000
        self.nbrDivVertical = 8
        self.nbrDivHorizontal = 10
        self.channelParameters = [{},{},{},{},{}]

    def connect(self, ip:string="128.178.201.10"):
        """
         Connect to the digital signal oscilloscope

         :param ip: The IP adress of the oscilloscope (default: 128.178.201.10)
         :type ip: string

         :Example:

         >>> osc = Osc.Oscilloscope()
         >>> osc.connect()

         .. seealso:: disconnect()
         .. warning:: Only works with LeCroy Wavesurfer 3024.
         .. todo:: Extend to other protocol and/or instruments
         """

        #visa.log_to_screen()
        self.rm = visa.ResourceManager()
        self.osc = self.rm.open_resource(f'VICP::{ip}::INSTR', resource_pyclass=MessageBasedResource)
        self.osc.timeout = 5000
        self.osc.clear()

        log.debug("HEADER disabling")
        self.write("COMM_HEADER OFF")
        self.write("COMM_FORMAT OFF,WORD,BIN")
        log.debug("HEADER disabled")
        self.write(r"""vbs 'app.settodefaultsetup' """)

    def printID(self):
        """
         Returns the identification string of the instrument (by politely asking it).

         :return: identification string
         :rtype: string

         :Example:

         >>> osc = Osc.Oscilloscope()
         >>> osc.connect()
         >>> osc.printID()

         .. todo:: update example

         """

        log.debug("Getting identifier of the osc")
        r = self.query('*IDN?', 2)

        log.info(r)
        return r

    def write(self, command:string):
        """
         Send a command to the instrument and blocks until the command has been processed.

         No validation of any sort will be done. Use it at your own risk.

         :param command: Command to send
         :type command: string

         :Example:

         >>> osc = Osc.Oscilloscope()
         >>> osc.connect()
         >>> osc.write("COMM_HEADER OFF")

         .. note:: This is a blocking call.
         .. todo:: Extend to work with other DSO
         """

        self.osc.write(command)
        r = self.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        log.debug(r)

    def query(self, command:string, timeout:int=None):
        r = self.osc.query(command)

        log.info(r)
        return r

    def setTrigger(self,triggerLevel:float=1,triggerDelay:float=0,channel:int=1,triggerMode:string="SINGLE", unitTriggerLevel:string="V"):
        """
        Changes trigger parameters

        :param triggerLevel: Level of the trigger
        :type triggerLevel: float
        :param triggerDelay: Delay of the trigger. The unit is the one specified in the setGrid() method.
        :type triggerDelay: string
        :param channel: Channel on which you need to set the trigger
        :type command: int
        :param triggerMode: Mode of the trigger. Either `AUTO`, `NORMAL`, `SINGLE` or `STOP`.
        :type triggerMode: string
        :param unitTriggerLevel: Unit for the trigger level. See setGrid() for available options.
        :type unitTriggerLevel: string

        .. seealso:: setGrid()

        """
        self.write(f'C{channel}:TRIG_LEVEL {triggerLevel}{unitTriggerLevel}')
        self.write(f'TRIG_DELAY {triggerDelay}')
        self.write(f'TRIG_MODE {triggerMode}')

    def setGrid(self, timeDivision:float=0.0001,voltDivision:float=1.0,channel:int=1,unitVoltDivision:string="V",unitTimeDivision:string="S"):
        """
        Changes grid parameters

        :param timeDivision: The time per division.
        :type timeDivision: float
        :param voltDivision: The voltage per division.
        :type voltDivision: float
        :param channel: The channel on which the modification must be applied. Has only effect on the voltage per division parameter.
        :type channel: int
        :param unitVoltDivision: Unit to apply to voltDivision (V, MV, UV)
        :type unitVoltDivision: string
        :param unitTimeDivision: Unit to apply to timeDivision (S, MS, US, NS)
        :type unitTimeDivision: string

        """

        self.channelParameters[channel]['volt_division'] = voltDivision
        self.channelParameters[channel]['time_division'] = timeDivision
        self.write(f'C{channel}:VOLT_DIV {voltDivision}{unitVoltDivision}')
        self.write(f'TIME_DIV {timeDivision}{unitTimeDivision}')
        self.write(f'C{channel}:TRACE ON')


    def acquire(self, dataOnly:bool=False, numpyFormat:bool=True, channel:int=1, forceAcquisition:bool=False, readOnly:bool=False):
        """
        Acquires the data on the Oscilloscope.

        The function returns a dictionnary containing the different informations
        about the waveform. It contains the following keys:

        + "description":
        + "text":
        + "time":
        + "data":
        + "channelParameters":

        These can be retrieved from a dictionnary

        :param dataOnly: If true, the function returns only the data block without any other information (not wrapped into a dictionnary)
        :type dataOnly: bool
        :param numpyFormat: If true, returns the data in a int16 numpy format.
        :type numpyFormat: bool
        :param channel: Channel to acquire.
        :type channel: int
        :param forceAcquisition: Manually force an acquisiion. Does not wait on the trigger.
        :type forceAcquisition: bool
        :param readOnly: Only reads the content of the buffer without arming the acquisiton
        :type readOnly: bool

        :return: A dictionnary containing the informations or an array with the datapoints
        :rtype: dictionnary or array

        :Example:

        To be added

        .. warning:: This function need more testing and maybe a refactoring of its parameters. Its mode of operation should be atomized in the future but this might stay to provide legacy compatibility.
        .. todo:: Atomize.
        """

        if readOnly==False:
            self.osc.write(f'ARM_ACQUISITION')
            self.osc.write(f'WAIT')

        if forceAcquisition:
            self.osc.write(f'FORCE_TRIGGER')

        self.osc.write(f'C{channel}:WAVEFORM? DESC')
        desc = self.osc.read_raw()
        #log.debug(f'Wave descriptor : {desc}')

        self.osc.write(f'C{channel}:WAVEFORM? TEXT')
        text = self.osc.read_raw()
        #log.debug(f'Wave text : {text}')

        self.osc.write(f'C{channel}:WAVEFORM? TIME')
        time = self.osc.read_raw()
        #log.debug(f'Wave time : {time}')

        data1 = self.osc.query_binary_values(f'C{channel}:WAVEFORM? DAT1', datatype='h', is_big_endian=False, header_fmt='ieee')
        #log.debug(f'Wave data 1 : {data1}')

        if numpyFormat :
            i = 0
            data = np.empty(len(data1), dtype=np.int16)
            for sample in data1:
                data[i]=sample
                i+=1
        else:
            data = data1

        if dataOnly :
            return data
        else:
            res = { "description" : desc, "text": text, "time" : time, "data" : data, "channelParameters":self.channelParameters[channel] }
            return res

    def disconnect(self):
        self.osc.close()
        self.rm.close()
