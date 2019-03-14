
BAUD_RATE = 115200

import serial
import logging as log

class SignalGeneratorWidget():

    def __init__(self, parent=None):


    def connect(port='COM4'):
        #Create an instrument object
        self.mSerialConnection = serial.Serial(port,BAUD_RATE) # Select the COM port of the Device

        self.mSerialConnection.write("\r\n\r\n") # flush
        self.mSerialConnection.flushInput()

        self.mSerialConnection.write("*IDN?\n")
        out = self.mSerialConnection.readline().strip()

        log.info("Identifier of the signal generator" + out)
        # MatLab code
        #s.Terminator = 'LF';                    % Configure the Terminator for the serial commands
        #s.InputBufferSize = 256013;             % Adjusts the input buffer size to the maximum points allowed by the WaveForm Generator TG2512A 128k points -> 256000 (2 Bytes per point) + 8 (#6128000) + 5  (ARB1 )
        #s.OutputBufferSize = 256013;            % Adjusts the input buffer size to the maximum points allowed by the WaveForm Generator TG2512A 128k points -> 256000 (2 Bytes per point) + 8 (#6128000) + 5  (ARB1 )
