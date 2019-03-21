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
 The ``SignalGenerator`` module
 ======================

 *Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
 *Last modification:* 21.03.2019

 This module is a class to handle a signal generator connected by serial
 over USB. It currently supports only the TG2512A from AimTTi.

 A few notes
 -------------------

### Sending data to signal generator.
 During the development, I remarked that the data have to be sent all at once.
 See the following :
 >>> self.mSerialConnection.write(bin)
 With bin containing 100% of the signal.

 """



BAUD_RATE = 115200

import serial
import logging as log
import string
import numpy as np

class SignalGenerator():

    def __init__(self, parent=None):
        log.info("New signal generator created")

    def connect(self,port:string="COM6"):
        """
         Connects the signal generator object to the real instrument by the mean
         of a serial connection.

         :param port: Port on which the signal generator is connected.
         :type port: string

         :Example:

         >>> signalG = SG.SignalGenerator()
         >>> signalG.connect(port="/dev/serial/by-id/usb-THURLBY_THANDAR_INSTRUMENTS_TG2512A_DA200678-if00")

         .. seealso:: disconnect()
         """

        self.port=port
        try:
            #Create an instringument object
            self.mSerialConnection = serial.Serial(port,BAUD_RATE,timeout=0.1) # Select the COM port of the Device
        except serial.SerialException:
            self.mSerialConnection.close()
        except:
            log.error("Somethong went wrong")
            self.mSerialConnection.close()

        self.mSerialConnection.write(("\r\n\r\n").encode()) # flush
        self.mSerialConnection.flushInput()

        self.mSerialConnection.write(("*IDN?\n").encode())
        out = self.mSerialConnection.readline().strip()

        # Reset parameters
        cmd = "RST\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug(cmd + " : OK\n")

        log.debug("Identifier of the signal generator : " + out.decode())
        # MatLab code
        #s.Terminator = 'LF';                    % Configure the Terminator for the serial commands
        #s.InputBufferSize = 256013;             % Adjusts the input buffer size to the maximum points allowed by the WaveForm Generator TG2512A 128k points -> 256000 (2 Bytes per point) + 8 (#6128000) + 5  (ARB1 )
        #s.OutputBufferSize = 256013;            % Adjusts the input buffer size to the maximum points allowed by the WaveForm Generator TG2512A 128k points -> 256000 (2 Bytes per point) + 8 (#6128000) + 5  (ARB1 )

    def disconnect(self):
        """
         Disconnect the signal generator object from the real instrument.

         :Example:

         >>> signalG = SG.SignalGenerator()
         >>> signalG.connect(port="/dev/serial/by-id/usb-THURLBY_THANDAR_INSTRUMENTS_TG2512A_DA200678-if00")
         >>> signalG.disconnect()

         .. seealso:: connect()
         """
        self.mSerialConnection.write(("BEEP\n").encode())
        self.mSerialConnection.write(("LOCAL\n").encode())
        self.mSerialConnection.close()
        self.mSerialConnection = 0

    def setChannel(self, channel:int=1):
        """
         Select the channel on which the following commands will apply.

         :param channel: Port on which the signal generator is connected.
         :type channel: int

         :Example:

         >>> signalG = SG.SignalGenerator()
         >>> signalG.connect(port="/dev/serial/by-id/usb-THURLBY_THANDAR_INSTRUMENTS_TG2512A_DA200678-if00")
         >>> signalG.setChannel(2)

         """
        self.mSerialConnection.write((f'CHN {channel}\n').encode())
        log.debug(f'Channel {channel} selected.')

    def setOutput(self, state:bool=True):
        """
         Set the output state.

         :param state: Port on which the signal generator is connected.
         :type state: bool

         :Example:

         >>> signalG = SG.SignalGenerator()
         >>> signalG.connect(port="/dev/serial/by-id/usb-THURLBY_THANDAR_INSTRUMENTS_TG2512A_DA200678-if00")
         >>> signalG.setChannel(2)
         >>> signalG.setOutput(True)
         """
        if state:
            cmd = "OUTPUT ON"
        else:
            cmd = "OUTPUT OFF"
        cmd = cmd + "\n"
        self.mSerialConnection.write(cmd.encode())

        log.debug(cmd)

    def setFrequency(self, frequency:int=1):
        """
         Set the frequency of the signal.

         :param frequency: Port on which the signal generator is connected.
         :type frequency: int

         :Example:

         >>> signalG = SG.SignalGenerator()
         >>> signalG.connect(port="/dev/serial/by-id/usb-THURLBY_THANDAR_INSTRUMENTS_TG2512A_DA200678-if00")
         >>> signalG.setChannel(2)
         >>> signalG.setFrequency(200)
         """
        cmd = "FREQ"
        cmd = cmd + " " + str(frequency) + "\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug("Frequency set to " + str(frequency) + " Hz : " + cmd)

    def setWave(self, wave:string="ARB", number:int=1):
        """
         Set the output waveform type to <SINE>, <SQUARE>, <RAMP>, <TRIANG>,
         <PULSE>, <NOISE>, <PRBSPN7>, <PRBSPN9>, <PRBSPN11>, <PRBSPN15>,
         <PRBSPN20>, <PRBSPN23> or <ARB>.

         :param wave: Type of waveform.
         :type wave: string

         :param number: Register number for the ARB waveform.
         :type number: int

         :Example:

         >>> signalG = SG.SignalGenerator()
         >>> signalG.connect(port="/dev/serial/by-id/usb-THURLBY_THANDAR_INSTRUMENTS_TG2512A_DA200678-if00")
         >>> signalG.setChannel(2)
         >>> signalG.setWave("ARB", 3)
         """
        cmd = "WAVE"
        cmd = cmd + " " + wave + "\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug("Wave setting : " + cmd)

        if(wave == "ARB"):
            cmd = "ARBLOAD"
            cmd = cmd + " ARB" + str(number) + "\n"
            self.mSerialConnection.write(cmd.encode())
            log.debug("ARB setting : " + cmd)



    def setArbitraryWaveform(self, data, register:int=1, name:string="ARB", callback=False):
        """
         Load data to an existing arbitrary waveform memory
         location ARB1. The data consists of two bytes per point
         with no characters between bytes or points. The point
         data is sent high byte first. The data block has a header
         which consists of the # character followed by several
         ascii coded numeric characters. The first of these defines
         the number of ascii characters to follow and these
         following characters define the length of the binary data
         in bytes. The instrument will wait for data indefinitely If
         less data is sent. If more data is sent the extra is
         processed by the command parser which results in a
         command error.

         :param data: Data to send. The data must be an array of uint16
         :param register: Register in which the data will be sent.
         :param name: Name of the waveform (for labelling on the instrument)
         :param callback: Callback to call at each increment in the sending process.

         :Example:

         >>> signalG = SG.SignalGenerator()
         >>> signalG.connect(port="/dev/serial/by-id/usb-THURLBY_THANDAR_INSTRUMENTS_TG2512A_DA200678-if00")
         >>> signalG.setChannel(2)
         >>> signalG.setWave("ARB", 3)
         >>> size = 1024
         >>> data = np.zeros(size, dtype=np.uint16)
         >>> for i in range(0, size-1):
         >>>    data[i] = 0.03*np.square(i)+0.01*i+1
         >>> signalG.setArbitraryWaveform(data, register=3, name="TEST_SQUARE3")

         .. seealso:: setWave()
         """
        header = "ARB" + str(register) + " " # TODO: add security for register numbers

        size=data.size

        sizeStr = str(2*size)

        log.debug("sizeStr = " + sizeStr)

        header = header + "#" + str(len(sizeStr)) + sizeStr

        #self.mSerialConnection.write(header.encode())

        log.debug("Header : " + header)

        dataHandler = np.uint16()

        percent = size/100
        percentAcc = percent

        bin = bytearray(header, 'utf-8')
        for i in range(0, size-1):
             dataHandler = data[i]
             bytesToSend = int(dataHandler).to_bytes(2, byteorder='big', signed=False)
             bin.append(bytesToSend[0])
             bin.append(bytesToSend[1])

        self.mSerialConnection.write(bin)

        self.mSerialConnection.write(("\n").encode())

        if(name != "ARB"):
            cmd = "ARBDEF " + "ARB" + str(register) + "," + name + "," + "OFF\n"
            self.mSerialConnection.write(cmd.encode())

    def setBurstMode(self, burstCount:int=1, burstPhase:float=0.0):
        """
         Set the signal generator into burst mode. You only need to call the
         ­``burst()`` method to send a pulse with the set wave.

         :param burstCount: The number of burst to send at each call of burst()
         :param burstPhase: The phase shift of the signal
         :type burstCount: int
         :type burstPhase: float
         :return: None
         :rtype: int

         .. seealso:: burst()
         """
        # Set burst count
        cmd = "BSTCOUNT"
        cmd = cmd + " " + str(burstCount) + "\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug(cmd + " : OK\n")

        # Set burst phase
        cmd = "BSTPHASE"
        cmd = cmd + " " + str(burstPhase) + "\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug(cmd + " : OK\n")

        # Set burst mode to N cycle (N=burstCount)
        cmd = "BST NCYC\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug(cmd + " : OK\n")


        # Set trigger source
        cmd = "TRGSRC MAN\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug(cmd + " : OK\n")


        # Set trigger output (into burst module)
        cmd = "TRGOUT BURST\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug(cmd + " : OK\n")

        # Activate synchronized output
        cmd = "SYNCOUT ON\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug(cmd + " : OK\n")

        # Set synchronized output to burst mode
        cmd = "SYNCTYPE BURST\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug(cmd + " : OK\n")

        log.info("Config for burst mode done.")

    def burst(self):
        """

        Send a burst.

         .. seealso:: setBurstMode()
         .. warning:: Use only acceptable after burst mode set
         """
        cmd = "*TRG\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug(cmd + " : OK\n")
        log.debug("BURST !")
