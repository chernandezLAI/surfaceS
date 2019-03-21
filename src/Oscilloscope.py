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
 *Last modification:* 21.03.2019

 This module is a class to handle an oscilloscope connected with on the LAN.
 It currently supports only the LeCroy Waverunner LT224.

 """



BAUD_RATE = 115200

import visa
import logging as log
import string
import numpy as np

class Oscilloscope():
    def __init__(self, parent=None):
        pass

    def connect(self, ip:string="128.178.201.59"):
        # DOES NOT WORK
        # TODO: fix
        self.rm = visa.ResourceManager()
        self.osc = self.rm.open_resource(f'TCPIP::{ip}::INSTR')
        self.osc.timeout = 5000
        self.osc.clear()

        self.osc.write("COMM_HEADER OFF")
        self.osc.write(r"""vbs 'app.settodefaultsetup' """)

    def disconnect(self):
        self.osc.close()
        self.rm.close()
