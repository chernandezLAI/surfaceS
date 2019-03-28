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
 The ``cnc`` module
 ======================

 This module controls the CNC. It provides a useful interface to send commands
 to the cnc while keeping the control asynchronous.

 """

import threading
import time

class CNC(threading.Thread):
    """docstring for ."""
    def __init__(self, arg):
        super(self).__init__()
        #threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
      print "Starting " + self.name
      print_time(self.name, 5, self.counter)
      print "Exiting " + self.name  
