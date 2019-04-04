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
 ======================

 *Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
 *Last modification:* 04.04.2019

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

log.basicConfig(level=log.DEBUG)

class Oscilloscope():
    def __init__(self, parent=None):
        self.nbrSamplesSeconde = 4000000000
        self.nbrDivVertical = 8
        self.nbrDivHorizontal = 10
        self.channelParameters = [{},{},{},{},{}]

    def connect(self, ip:string="128.178.201.10"):
        #visa.log_to_screen()

        self.rm = visa.ResourceManager()
        self.osc = self.rm.open_resource(f'VICP::{ip}::INSTR', resource_pyclass=MessageBasedResource)
        #self.osc = self.rm.open_resource(f'TCPIP0::{ip}::INSTR')
        self.osc.timeout = 5000
        #self.osc.set_visa_attribute(visa.attributes.VI_ATTR_IO_PROT,visa.constants.VI_PROT_4882_STRS)
        #self.osc.io_protocol = 4
        self.osc.clear()

        log.debug("HEADER disabling")
        self.write("COMM_HEADER OFF")
        self.write("COMM_FORMAT OFF,WORD,BIN")
        log.debug("HEADER disabled")
        self.write(r"""vbs 'app.settodefaultsetup' """)
        #self.osc.read()

    def printID(self):
        #self.osc.write('AUTO_SETUP')
        log.debug("Getting identifier of the osc")
        r = self.query('*IDN?', 2)

        log.info(r)
        return r

    def write(self, command:string):
        self.osc.write(command)
        r = self.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
        log.debug(r)

    def query(self, command:string, timeout:int=None):
        r = self.osc.query(command)

        log.info(r)
        return r

    def setTrigger(self,triggerLevel:int=1,triggerDelay:int=0,channel:int=1,triggerMode:string="SINGLE", unitTriggerLevel:string="V"):
        """
         Changes trigger parameters

         .. todo:: Make it better.
         """
        self.write(f'C{channel}:TRIG_LEVEL {triggerLevel}{unitTriggerLevel}')
        self.write(f'TRIG_DELAY {triggerDelay}')
        self.write(f'TRIG_MODE {triggerMode}')

    def setGrid(self, timeDivision:int=0.0001,voltDivision:int=1,channel:int=1,unitVoltDivision:string="V",unitTimeDivision:string="S"):
        """
         Changes grid parameters

         .. todo:: Make it better.
         """
        self.channelParameters[channel]['volt_division'] = voltDivision
        self.channelParameters[channel]['time_division'] = timeDivision
        self.write(f'C{channel}:VOLT_DIV {voltDivision}{unitVoltDivision}')
        self.write(f'TIME_DIV {timeDivision}{unitTimeDivision}')


    def acquire(self, dataOnly:bool=False, numpyFormat=True, channel:int=1):
        """
         function directly created from
         ``Oscilloscopes Remote Control and Automation Manual``

         .. todo:: Make it better.
         """
        self.osc.write(f'ARM_ACQUISITION')
        self.osc.write(f'WAIT')

        self.osc.write(f'C{channel}:WAVEFORM? DESC')
        desc = self.osc.read_raw()
        log.info(f'Wave descriptor : {desc}')

        self.osc.write(f'C{channel}:WAVEFORM? TEXT')
        text = self.osc.read_raw()
        log.info(f'Wave text : {text}')

        self.osc.write(f'C{channel}:WAVEFORM? TIME')
        time = self.osc.read_raw()
        log.info(f'Wave time : {time}')

        data1 = self.osc.query_binary_values(f'C{channel}:WAVEFORM? DAT1', datatype='h', is_big_endian=False, header_fmt='ieee')
        log.info(f'Wave data 1 : {data1}')

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
