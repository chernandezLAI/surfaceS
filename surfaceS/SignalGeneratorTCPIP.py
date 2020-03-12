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
        cmd = "*IDN?"
        out = self.sg.query(cmd)
        log.info(out)

        # Reset parameters
        cmd = "*RST"
        self.sg.write(cmd)


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
        cmd = "*IDN?"
        r = self.sg.query(cmd)
        log.info(r)
        return r

    def disconnect(self):
        """
         Disconnect from the signalG.

         """
        self.sg.close()
        self.rm.close()

    def beep(self):
        """
         Ask the Equipment to BEEP one time.

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.beep()

         """
        cmd = "BEEP"
        self.sg.write(cmd)
        log.debug('Request to BEEP Sent')

    def setChannel(self, channel:int=1):
        """
         Select the channel on which the following commands will apply.

         :param channel: Port on which the signal generator is connected.
         :type channel: int

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(2)

         """
        self.sg.write(f'CHN {channel}')
        log.debug(f'Channel {channel} selected.')

    def setOutput(self, state:bool=True):
        """
         Set the output state.

         :param state: Port on which the signal generator is connected.
         :type state: bool

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(2)
         >>> signalG.setOutput(True)
         """
        if state:
            cmd = "OUTPUT ON"
        else:
            cmd = "OUTPUT OFF"
        self.sg.write(cmd)
        log.debug(cmd)

    def setFrequency(self, frequency:float=1.0):
        """
         Set the frequency of the signal.

         :param frequency: Frequency for the signal Hz.
         :type frequency: float

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(2)
         >>> signalG.setFrequency(200)

         .. seealso:: setPulseFrequency()
         """
        cmd = "FREQ"
        cmd = cmd + " " + str(frequency)
        self.sg.write(cmd)
        log.debug("Frequency set to " + str(frequency) + " Hz : " + cmd)

    def setTrigger(self, trgsrc="MAN"):
        """
         Set the trigger source for the channel that is actively selected. Select
         "CRC" to let the other channel trigger the selected channel.

         :param frequency: Trigger source <INT>, <EXT>, <CRC> or <MAN>.
         :type frequency: string

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(2)
         >>> signalG.setTrigger("CRC")

         .. seealso:: burst() and setBurstMode()
         .. warning:: Use only acceptable after burst mode set
         """
        cmd = "TRGSRC"
        cmd = cmd + " " + str(trgsrc)
        self.sg.write(cmd)
        log.debug("Trigger source set to " + str(trgsrc) + " : " + cmd)

    def setPulseFrequency(self, frequency:float=1.0):
        """
         Set the frequency of the signal.

         :param frequency: Frequency for the pulse signal Hz.
         :type frequency: float

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(2)
         >>> signalG.setPulseFrequency(200)

         .. seealso:: setFrequency()
         """
        cmd = "PULSFREQ"
        cmd = cmd + " " + str(frequency)
        self.sg.write(cmd)
        log.debug("Pulse Frequency set to " + str(frequency) + " Hz : " + cmd)

    def setPulse(self, frequency:float=1.0, amplitude:float=1.0, unit="VPP", dcoffs:float=0.0, pulswid:float=1.0, pulsdly:float=0.0):
        """
         Set the a pulse output in the specified channel. It is IMPORTANT to
         consider that the max frequency that can be set is limited by the pulse
         width and pulse delay.

         :param frequency: Frequency for the signal Hz.
         :type frequency: float
         :param amplitude: amplitude of the signal in Volts by default it is 1.0 VPP.
         :type amplitude: float
         :param unit: Unit specified for the amplitude <VPP>, <VRMS> or <DBM> by default it is VPP.
         :type unit: string
         :param dcoffs: DC offset of the signal in Volts by default it is 0.0 V.
         :type dcoffs: float
         :param pulswid: width of the pulse in seconds.
         :type pulswid: float
         :param pulsdly: Delay of the pulse t setart in seconds.

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setPulse(5.0, 2.5, "VPP", 1.25, 0.023, 0.104)
         """
        self.setWave("PULSE")
        self.setPulseFrequency(frequency)
        self.setAmplitude(amplitude, unit, dcoffs)

        cmd = "PULSWID"
        cmd = cmd + " " + str(pulswid)
        self.sg.write(cmd)
        log.debug("Pulse width set to " + str(pulswid) + " Sec : " + cmd)

        cmd = "PULSDLY"
        cmd = cmd + " " + str(pulsdly)
        self.sg.write(cmd)
        log.debug("Pulse delay set to " + str(pulsdly) + " Sec : " + cmd)

        log.info("Config pulse done.")

    def setAmplitude(self, amplitude:float=1.0, unit="VPP", dcoffs:float=0.0):
        """
         Set the amplitude of the signal.

         :param amplitude: amplitude of the signal in Volts by default it is 1.0 VPP.
         :type amplitude: float
         :param unit: Unit specified for the amplitude <VPP>, <VRMS> or <DBM> by default it is VPP.
         :type unit: string
         :param dcoffs: DC offset of the signal in Volts by default it is 0.0 V.
         :type dcoffs: float

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(2)
         >>> signalG.setAmplitude(2.5, "VPP",1.25)
         """
        cmd = "AMPUNIT"
        cmd = cmd + " " + unit
        self.sg.write(cmd)
        cmd = "AMPL"
        cmd = cmd + " " + str(amplitude)
        self.sg.write(cmd)
        cmd = "DCOFFS"
        cmd = cmd + " " + str(dcoffs)
        self.sg.write(cmd)

        log.debug("Amplitude set to " + str(amplitude) + " " + unit + "with a DC offset of " + str(dcoffs) + " V : " + cmd)

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

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(2)
         >>> signalG.setWave("ARB", 3)
         """
        cmd = "WAVE"
        cmd = cmd + " " + wave
        self.sg.write(cmd)
        log.debug("Wave setting : " + cmd)

        if(wave == "ARB"):
            cmd = "ARBLOAD"
            cmd = cmd + " ARB" + str(number)
            self.sg.write(cmd)
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

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(2)
         >>> signalG.setWave("ARB", 3)
         >>> size = 1024
         >>> data = np.zeros(size, dtype=np.uint16)
         >>> for i in range(0, size-1):
         >>>    data[i] = 0.03*np.square(i)+0.01*i+1
         >>> signalG.setArbitraryWaveform(data, register=3, name="TEST_SQUARE3")

         .. seealso:: setWave()
         """

        data = np.interp(data, [data.min(), data.max()], [0, 16381]) #Scale the data to the range o the Signal generator
        header = "ARB" + str(register) + " " # TODO: add security for register numbers

        size=data.size

        sizeStr = str(2*size)

        log.debug("sizeStr = " + sizeStr)

        header = header + "#" + str(len(sizeStr)) + sizeStr

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

        cmd = bytes(bin)
        self.sg.write_raw(cmd)
        self.sg.write('\n')

        log.info("Signal uploaded.")

        if name != "ARB":
            cmd = "ARBDEF " + "ARB" + str(register) + "," + name + "," + "OFF"
            self.sg.write(cmd)
            log.debug(f'Name set: {name}')

    def setBurstMode(self, burstCount:int=1, burstPhase:float=0.0):
        """
         Set the signal generator into burst mode. You only need to call the
         ­``burst()`` method to send a N pulses with the set wave (N = burstCount).

         :param burstCount: The number of burst to send at each call of burst()
         :param burstPhase: The phase shift of the signal (NOT AVAILABLE AT THE MOMENT)
         :type burstCount: int
         :type burstPhase: float (NOT AVAILABLE AT THE MOMENT)

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(1)
         >>> signalG.setBurstMode(1)


         .. seealso:: burst()
         """
        # Set burst count
        cmd = "BSTCOUNT"
        cmd = cmd + " " + str(burstCount)
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")

        # # Set burst phase
        # cmd = "BSTPHASE"
        # cmd = cmd + " " + str(burstPhase)
        # self.sg.write(cmd)
        # log.debug(cmd + " : OK\n")

        # Set burst mode to N cycle (N=burstCount)
        cmd = "BST NCYC"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")


        # Set trigger source
        cmd = "TRGSRC MAN"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")


        # Set trigger output (into burst module)
        cmd = "TRGOUT BURST"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")

        # Activate synchronized output
        cmd = "SYNCOUT ON"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")

        # Set synchronized output to burst mode
        cmd = "SYNCTYPE BURST"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")

        log.info("Config for burst mode done.")

    def setTriggerSignal(self, OUTchannel:int=1):
        """
         Set the signal generator to output a short squared pulse in the other
         output (The opposite to the one set in setChannel()) to trigger the acquisition
         on the other devices. The trigger signal is a pulse of 5 v and has a pulse length of 10 ms

         :param channel: Port that was selected for the main output of the signal
          generator with setChannel().
         :type channel: int

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(2)
         >>> signalG.setTriggerSignal(2)


         .. seealso:: setChannel()
        """
        if OUTchannel == 1:
            TRIGchannel = 2
        else:
            TRIGchannel = 1
        # Select the channel for the trigger OUTPUT
        self.setChannel(TRIGchannel)
        # SetUp the trigger signal
        self.setWave("PULSE")
        self.setPulse(5.0, 2.5, "VPP", 1.25, 0.01)

        # Set burst count
        cmd = "BSTCOUNT"
        cmd = cmd + " " + str(1)
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")

        # Set burst mode to N cycle (N=burstCount)
        cmd = "BST NCYC"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")

        # Set trigger source
        cmd = "TRGSRC CRC"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")

        # Set trigger output (into burst module)
        cmd = "TRGOUT BURST"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")

        # Activate synchronized output
        cmd = "SYNCOUT ON"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")

        # Set synchronized output to burst mode
        cmd = "SYNCTYPE BURST"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")

        # Set the equipment back to hte output channel.
        self.setChannel(OUTchannel)

        log.info("Config for additional trigger OK.")





    def burst(self):
        """

        Send or Trigger a burst.

         :Example:

         >>> import SignalGeneratorTCPIP as SG
         >>> signalG = SG.SignalGeneratorTCPIP()
         >>> signalG.connect()
         >>> signalG.setChannel(1)
         >>> signalG.setBurstMode(1)
         >>> signalG.burst()

         .. seealso:: setBurstMode()
         .. warning:: Use only acceptable after burst mode set
         """
        cmd = "*TRG"
        self.sg.write(cmd)
        log.debug(cmd + " : OK\n")
        log.debug("BURST !")

# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused impor
from matplotlib import cm
import matplotlib.animation as animation

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt5 import QtCore, QtWidgets

class SignalPlot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)

        FigureCanvas.__init__(self, self.fig)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.ax = self.fig.add_subplot(111)

        self.ready = True

    def plot(self, data):
        # discards the old graph
        self.ax.clear()

        # plot data
        self.ax.plot(data, '*-')

        # refresh canvas
        self.draw()


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
