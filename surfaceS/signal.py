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
 The ``Signal` module
 ======================

 *Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
 *Last modification:* 18.04.2019

 Scenario 1

 """

#import threading
#import time
#import queue
#import logging as log
#import string
#import serial

#from surfaceS import Oscilloscope as Osc
#from surfaceS import SignalGenerator as SG
#from surfaceS import cnc as CNC



class Signal():
    def __init__(self, data, sampling_freq, amplitude_max):
        self.datapoints = data
        self.sampling_freq = sampling_freq
        self.amplitude_max = amplitude_max

    def get_points
