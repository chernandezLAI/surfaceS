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
    The ``SignalGeneratorTCPIP`` module
    ==============================

    *Author:* [Camilo Hernandez](mailto:camilo.hernandez@epfl.ch)
    *Last modification:* 22.11.2019

    This module is a class to handle a signal generator connected by TCPIP (LAN or Ethernet).
    It currently supports only the TG2512A from AimTTi.

    A few notes
    -------------------

    ### Sending data to signal generator.
    During the development, Jeremy Jayet remarked that the data have to be sent all at once.
    See the following :
    >>> self.mSerialConnection.write(bin)
    With bin containing 100% of the signal.

"""
import visa

import logging as log
import string
import numpy as np

class SignalGeneratorTCPIP():

    def __init__(self, parent=None):
        log.info("New signal generator created")

    def connect(self, ip:str="128.178.201.37", port:str="9221"):
        """
         Connects the signal generator object to the real instrument by the mean
         of an ethernet connection (LAN or TCPIP).

         :param ip: The IP adress of the Signal Generator (default: 128.178.201.37)
         :type ip: string

         :param port: The port at which the Signal Generator is listening (default: 9221)
         :type port: string

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()

         .. seealso:: disconnect()
         .. warning:: Only tested for the Signal generator (Waveform Generator) TG2512A from AimTTi
         """

        self.rm = visa.ResourceManager()
        self.sg = self.rm.open_resource(f'TCPIP0::{ip}::{port}::SOCKET', read_termination='\n', write_termination = '\n')
        log.debug("Getting identifier of the signalG")
        out = self.sg.query('*IDN?')
        log.info(out)

        # Reset parameters
        self.sg.write('*RST')


    def printID(self):
        """
         Returns the identification string of the instrument (by politely asking it).

         :return: identification string
         :rtype: string

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.printID()

         """

        log.debug("Getting identifier of the signalG")
        r = self.sg.query('*IDN?')
        log.info(r)
        return r

    def beep(self):
        """
         Ask the Equipment to BEEP one time.

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.beep()

         """
        self.sg.write('BEEP')
        log.debug("Request to BEEP Sent")

    def disconnect(self):
        """
         Disconnect from the signalG.

         """
        self.sg.close()
        self.rm.close()

#
# rm = visa.ResourceManager()
# print(rm)
# sg = rm.open_resource('TCPIP0::128.178.201.37::9221::SOCKET', read_termination='\n', write_termination = '\n')
# sg.query('*IDN?')
#
# #%%
# sg.write('BEEP')
# sg.write('CHN 1')
# sg.write('WAVE PULSE')
# sg.write('PULSFREQ 4')
# sg.write('AMPUNIT VPP')
# sg.write('AMPL 2.5')
# sg.write('DCOFFS 1.25')
# sg.write('PULSWID 0.04')
# sg.write('PULSDLY 0')
#
# sg.write('CHN 2')
# sg.write('WAVE PULSE')
# sg.write('PULSFREQ 4')
# sg.write('AMPUNIT VPP')
# sg.write('AMPL 2.5')
# sg.write('DCOFFS 1.25')
# sg.write('PULSWID 0.023')
# sg.write('PULSDLY 0.104')
# #sg.write('')
# #sg.write('')
#
# #%%
#
# sg.close()
# rm.close()
