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

RX_BUFFER_SIZE = 128
BAUD_RATE = 115200
ENABLE_STATUS_REPORTS = True
REPORT_INTERVAL = 1.0 # seconds
EOLStr ='\n'

import threading
import time
from asyncio import Queue

class Cnc(threading.Thread):
    """docstring for ."""
    def __init__(self, arg):
        super(self).__init__()
        self.threadID = threadID
        self.name = name
        self.commandQueue = Queue()
        #self.queueLock = threading.Lock()
        self.running = False

    def run(self):
        self.running = True

        # Initialize
        cnc = serial.Serial(args.device_file,BAUD_RATE)

        # Wake up grbl
        log.info("Initializing Grbl...")
        cnc.write("\r\n\r\n")

        # Wait for grbl to initialize and flush startup text in serial input
        time.sleep(2)
        cnc.flushInput()

        while running :
            #self.queueLock.acquire()
            while self.commandQueue.empty() == False :
                cmd = self.commandQueue.get().strip() + EOLStr
                cnc.write(cmd.encode())

                out = cnc.readline().strip() # Wait for grbl response
                if out.find('ok') < 0 and out.find('error') < 0 :
                    log.info('MSG: {out}') # Debug response
                else :
                    if out.find('error') >= 0 :
                        log.error('ERROR: {out}')

    def periodic_timer() :
        while self.running:
          send_status_query()
          time.sleep(REPORT_INTERVAL)

    def sendCommand(self, command:string="?"):
        commandQueue.put(command)
        #self.queueLock.release()
        pass

    def jog(self, axis:string="x", distance:float=1):
        self.sendCommand("G91")
        axis.capitalize()
        self.sendCommand(f'G0 {axis}{distance}')

    def goTo(self, x:float=9999,y:float=9999,z:float=9999, feedrate:int=1000):
        self.sendCommand("G90")
        command = " "
        if x != 9999:
            command += f'X{x} '

        if y != 9999:
            command += f'Y{y} '

        if z != 9999:
            command += f'Z{z} '

        command += f'F{feedrate}'
        self.sendCommand(f'G1{command}')

    def home(self):
        self.sendCommand("$H")
    def unlock(self):
        self.sendCommand("$X")

    def updateStatusCallback(self, cb=self.printStatus):
        statusCallback = cb
