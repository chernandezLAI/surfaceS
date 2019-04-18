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

 *Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
 *Last modification:* 11.04.2019

 This module controls the CNC. It provides a useful interface to send commands
 to the cnc while keeping the control asynchronous.

 """

RX_BUFFER_SIZE = 128
BAUD_RATE = 115200
ENABLE_STATUS_REPORTS = True
REPORT_INTERVAL = 1.0 # seconds
EOLStr ='\n'

DEVICE_DEFAULT = "COM5"

import threading
import time
import queue
import logging as log
import string
import serial

# Experimental values
SOFT_LIMIT_X_P = -47.0
SOFT_LIMIT_X_N = -420.0
SOFT_LIMIT_Y_P = -2.0
SOFT_LIMIT_Y_N = -582.0
SOFT_LIMIT_Z_P = -2.0
SOFT_LIMIT_Z_N = -119.0

class Cnc(threading.Thread):
    def __init__(self, threadID=0, name="cnc_controller"):
        log.basicConfig(level=log.DEBUG)
        super(Cnc, self).__init__()
        self.threadID = threadID
        self.name = name
        self.commandQueue = queue.Queue()
        self.running = False
        self.deviceFile = DEVICE_DEFAULT
        self.cncLock = threading.Lock()
        self.setPositionEvent(threading.Event(), 0, 0)
        self.x = 9999
        self.y = 9999
        self.z = 9999

        self.workingZeroX = 0.0
        self.workingZeroY = 0.0
        self.workingZeroZ = 0.0

        def printStatus(state, x, y, z):
            print(f'{state}, {x}, {y}, {z}')
        self.statusCallback = printStatus

    def run(self):
        self.cncLock.acquire()
        self.running = True

        # Initialize
        self.cnc = serial.Serial(self.deviceFile,BAUD_RATE)

        self.updaterThread = threading.Thread(target=self.periodic_timer)
        self.updaterThread.start()

        # Wake up grbl
        log.info("Initializing Grbl...")
        cmd = "\r\n\r\n"
        self.cnc.write(cmd.encode())

        # Wait for grbl to initialize and flush startup text in serial input
        time.sleep(2)
        self.cnc.flushInput()
        self.cncLock.release()

        while self.running :
            cmd = self.commandQueue.get().strip() + EOLStr
            if self.running == False:
                break
            self.cncLock.acquire()
            self.cnc.write(cmd.encode())

            out = str(self.cnc.readline().strip()) # Wait for grbl response
            if out.find('ok') >= 0 :
                log.debug(f'MSG: {out}') # Debug response
            elif out.find('error') >= 0 :
                log.error(f'ERROR: {out}')
            else:
                log.info(out)
            self.cncLock.release()

        log.debug("CNC main loop left")
        self.cnc.close()
    def periodic_timer(self):
        while self.running:
          self.sendStatusQuery()
          time.sleep(REPORT_INTERVAL)

    def sendCommand(self, command:string="?"):
        self.commandQueue.put(command)
        #self.queueLock.release()
        pass

    def jog(self, axis:string="x", distance:float=1):
        self.sendCommand("G91")
        axis.capitalize()
        self.sendCommand(f'$J={axis}{distance} F1000')

    def goTo(self, x:float=9999,y:float=9999,z:float=9999, feedrate:int=1000, event:threading.Event=None):
        self.sendCommand("G90")
        command = " " # Do not delete the whitespace !
        if x != 9999:
            command += f'X{x} '

        if y != 9999:
            command += f'Y{y} '

        if z != 9999:
            command += f'Z{z} '

        command += f'F{feedrate}'
        self.sendCommand(f'G53 G1{command}') # Uses machine coordinates !!!!!!!!!!!

        if event != None:
            self.setPositionEvent(event, x, y)

    def goToWorking(self, x:float=9999,y:float=9999,z:float=9999, feedrate:int=1000, event:threading.Event=None):
        self.sendCommand("G90")
        command = " " # Do not delete the whitespace !
        if x != 9999:
            command += f'X{x} '

        if y != 9999:
            command += f'Y{y} '

        if z != 9999:
            command += f'Z{z} '

        command += f'F{feedrate}'
        self.sendCommand(f'G54 G1{command}') # Uses working coordinates !!!!!!!!!!!

        if event != None:
            self.setPositionEvent(event, x, y)

    def home(self):
        self.sendCommand("$H")
    def unlock(self):
        self.sendCommand("$X")

    def connect(self, device:string):
        self.deviceFile = device

    def stop(self):
        log.debug("CNC thread stopping...")
        self.sendCommand("?")
        self.running = False
        self.join()
        log.debug("CNC thread stopped")

    def __del__(self):
        self.stop()

    def updateStatusCallback(self, cb):
        self.statusCallback = cb

    def setPositionEvent(self, event:threading.Event, X, Y):
        self.positionEvent = event
        self.targetX = X
        self.targetY = Y

    def getState(self):
        return self.state

    def getMachineCoordinates(self):
        return (self.x, self.y, self.z)

    def zeroWorkingCoordinates(self):
        self.workingZeroX = self.x
        self.workingZeroY = self.y
        self.workingZeroZ = self.z

        self.sendCommand("G10 L20 P1 X0 Y0 Z0")

    def sendStatusQuery(self):
        self.cncLock.acquire()
        cmd="?"
        self.cnc.flushInput()
        self.cnc.write(cmd.encode())
        out = str(self.cnc.readline().strip()) # Wait for grbl response
        self.cncLock.release()
        log.debug(f'Status query: {out}')

        # Parsing
        idxBegin = out.find("<")
        idxEnd = out.find(">", idxBegin)
        if (idxBegin >= 0) and (idxEnd >= 0):
            out = out[idxBegin:idxEnd]
            log.debug("Parsing...")
            pars1 = out.split("|")
            pars2 = pars1[1].split(":")
            pars3 = pars2[1].split(",")
            s = pars1[0][1:].upper()
            X=float(pars3[0])
            Y=float(pars3[1])
            Z=float(pars3[2])
            workingX = X - self.workingZeroX
            workingZ = Z - self.workingZeroZ
            workingY = Y - self.workingZeroY
            self.statusCallback(state=s, x=workingX, y=workingY,z=workingZ)
            self.state = s
            self.x = X
            self.y = Y
            self.z = Z

        diffX = self.targetX - self.x
        diffY = self.targetY - self.y
        if (diffX < 0.5) and (diffY < 0.5):
            self.positionEvent.set()
