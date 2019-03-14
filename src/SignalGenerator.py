
BAUD_RATE = 115200

import serial
import logging as log
import string
import numpy as np

class SignalGenerator():

    def __init__(self, parent=None):
        log.info("New signal generator created")

    def connect(self,port:string="COM6"):
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

        log.debug("Identifier of the signal generator : " + out.decode())
        # MatLab code
        #s.Terminator = 'LF';                    % Configure the Terminator for the serial commands
        #s.InputBufferSize = 256013;             % Adjusts the input buffer size to the maximum points allowed by the WaveForm Generator TG2512A 128k points -> 256000 (2 Bytes per point) + 8 (#6128000) + 5  (ARB1 )
        #s.OutputBufferSize = 256013;            % Adjusts the input buffer size to the maximum points allowed by the WaveForm Generator TG2512A 128k points -> 256000 (2 Bytes per point) + 8 (#6128000) + 5  (ARB1 )

    def disconnect(self):
        self.mSerialConnection.write(("BEEP\n").encode())
        self.mSerialConnection.write(("LOCAL\n").encode())
        self.mSerialConnection.close()
        self.mSerialConnection = 0

    def setChannel(self, channel:int=1):
        self.mSerialConnection.write((f'CHN {channel}\n').encode())
        log.debug(f'Channel {channel} selected.')

    def setOutput(self, state:bool=True):
        if state:
            cmd = "OUTPUT ON"
        else:
            cmd = "OUTPUT OFF"
        cmd = cmd + "\n"
        self.mSerialConnection.write(cmd.encode())

        log.debug(cmd)

    def setFrequency(self, frequency:int=1):
        cmd = "FREQ"
        cmd = cmd + " " + str(frequency) + "\n"
        self.mSerialConnection.write(cmd.encode())
        log.debug("Frequency set to " + str(frequency) + " Hz : " + cmd)

    def setWave(self, wave:string="ARB", number=1):
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

        # for i in range(0, size-1):
        #     self.mSerialConnection.reset_input_buffer()
        #     dataHandler = data[i]
        #     bytesToSend = int(dataHandler).to_bytes(2, byteorder='big', signed=False)
        #     log.debug("Byte 1 : " + str(bytesToSend[0]) + ", byte 2 : " + str(bytesToSend[1]))
        #     self.mSerialConnection.write(bytesToSend[0])
        #     log.debug(self.mSerialConnection.read(1))
        #     self.mSerialConnection.write(bytesToSend[1])
        #     log.debug(self.mSerialConnection.read(1))
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

    def pulse(self):
        log.debug("PULSE")
