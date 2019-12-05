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
 The ``GUI`` module
 ======================

 *Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
 *Last modification:* 05.06.2019

 This module implements the different features of the GUI. The layout itself is
 described in the [mainwindow.ui](ui/mainwindow.ui) file.

 """

from PyQt5.QtWidgets import (QApplication, QMainWindow, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QMessageBox, QFileDialog)

import sys
import logging as log
import json
import pandas as pd
import numpy as np

from ui.mainwindow import Ui_MainWindow as MainWindow

import matplotlib as plt
# Make sure that we are using QT5
plt.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import Oscilloscope as Osc
import SignalGeneratorTCPIP as SG
import cnc as CNC
import measure_vibrations as mv
import mainPlot
import ExperimentParametersIO as ExpParamIO
import MeasureDataset

class Gui(QMainWindow, MainWindow):
    def __init__(self, parent=None):
        """
        Initialize the main window.

        """

        super(Gui, self).__init__(parent)
        log.debug('Preparing GUI...')
        self.setupUi(self)

        self.isOscilloscopeConnected = False
        self.isCncConnected = False
        self.isSignalGeneratorConnected = False

        self.signal = None

        self.experimentParameters = {}
        self.setExperimentParameters(ExpParamIO.getDefaultParameters())

        self.jsonFormatParameters.textChanged.connect(self.updateExpParams)

        self.sg = SG.SignalGeneratorTCPIP()
        self.osc = Osc.Oscilloscope()
        self.cnc = CNC.Cnc()

#################################### CNC #######################################

        self.cnc_step = 1

        def setCncStep():
            self.cnc_step = float(self.stepEdit.text())
        def jogXPlus():
            self.cnc.jog("x", self.cnc_step)
        def jogXMinus():
            self.cnc.jog("x", -1*self.cnc_step)
        def jogYPlus():
            self.cnc.jog("y", self.cnc_step)
        def jogYMinus():
            self.cnc.jog("y", -1*self.cnc_step)
        def jogZPlus():
            self.cnc.jog("z", self.cnc_step)
        def jogZMinus():
            self.cnc.jog("z", -1*self.cnc_step)
        def goToZeroCNC():
            self.cnc.goToWorking(0,0,0)

        self.connectCNCButton.clicked.connect(self.connectCNC)
        self.portCNCEdit.setText(self.experimentParameters['cnc_port'])

        self.homeButton.clicked.connect(self.cnc.home)

        self.stepEdit.textChanged.connect(setCncStep)

        self.positiveXButton.clicked.connect(jogXPlus)
        self.negativeXButton.clicked.connect(jogXMinus)
        self.positiveYButton.clicked.connect(jogYPlus)
        self.negativeYButton.clicked.connect(jogYMinus)
        self.positiveZButton.clicked.connect(jogZPlus)
        self.negativeZButton.clicked.connect(jogZMinus)

        self.unlockButton.clicked.connect(self.cnc.unlock)

        self.zeroWorkingCoordinatesButton.clicked.connect(self.cnc.zeroWorkingCoordinates)

        self.goToWorkingZeroButton.clicked.connect(goToZeroCNC)

        self.homeButton.setEnabled(False)
        self.stepEdit.setEnabled(False)
        self.positiveXButton.setEnabled(False)
        self.negativeXButton.setEnabled(False)
        self.positiveYButton.setEnabled(False)
        self.negativeYButton.setEnabled(False)
        self.positiveZButton.setEnabled(False)
        self.negativeZButton.setEnabled(False)
        self.unlockButton.setEnabled(False)
        self.zeroWorkingCoordinatesButton.setEnabled(False)
        self.goToWorkingZeroButton.setEnabled(False)

        def setStartCoordinates():
            (x, y, z) = self.cnc.getMachineCoordinates()
            self.startMachineCoordinatesEdit.setText(f'{x},{y},{z}')
            self.experimentParameters['start_x'] = x
            self.experimentParameters['start_y'] = y
            self.experimentParameters['start_z'] = z
            self.setExperimentParameters(self.experimentParameters)
        self.setStartCoordinatesButton.clicked.connect(setStartCoordinates)

        self.startMeasuringButton.clicked.connect(self.startMeasuring)

        self.createPlot()

        self.maxZLineEdit.textChanged.connect(self.update_plot_limits)
        self.minZLineEdit.textChanged.connect(self.update_plot_limits)

        self.saveFigureButton.clicked.connect(self.save_main_plot)

        self.actionOpenDataFile.triggered.connect(self.selectDataFile)

        self.actionOpenExperimentFile.triggered.connect(self.selectExperimentFile)

        self.actionSaveExperimentFile.triggered.connect(self.saveExperimentFile)

        self.timeSlider.valueChanged[int].connect(self.update_plot_in_time)

        self.connectOscilloscopeButton.clicked.connect(self.connectOsc)
        self.oscilloscopeIPEdit.setText(self.experimentParameters['osc_ip'])

        self.sgConnectButton.clicked.connect(self.connectSg)
        self.sgSerialPortEdit.setText(self.experimentParameters['sg_ip'])

        def change_CNC_Port(port):
            self.experimentParameters["cnc_port"] = port
            self.jsonFormatParameters.setPlainText(ExpParamIO.toJSONFromExpParams(self.experimentParameters))
            #self.updateExpParams()


        self.portCNCEdit.textChanged.connect(change_CNC_Port)

        self.createSignalPlot()

        self.sgChooseFileButton.clicked.connect(self.selectSignalFile)
        self.sgSendButton.clicked.connect(self.sendSignalToSignalGenerator)

        #self.osc.connect(self.experimentParameters['osc_ip'])
        #self.sg.connect(self.experimentParameters['sg_ip'])

        self.destroyed.connect(self.closeRessources)

################################################################################
#
# Setup the oscilloscope.
#
################################################################################

    def connectOsc(self):
        """
         Connect the oscilloscope object to the real instrument.

         Also check for errors.

         """
        if self.isOscilloscopeConnected == False:
            try:
                self.osc.connect(self.experimentParameters['osc_ip'])
                self.isOscilloscopeConnected = True
                self.connectOscilloscopeButton.setText("Disconnect")

            except Exception as e:
                msg = QMessageBox()
                self.error(str(e), "Error oscilloscope")
        else:
            self.osc.disconnect()
            self.connectOscilloscopeButton.setText("Connect")
            self.isOscilloscopeConnected = False

################################################################################
#
# Setup the signal generator.
#
################################################################################

    def connectSg(self):
        """
         Connect the signal generator object to the real instrument.

         Also check for errors.

         """
        if self.isSignalGeneratorConnected == False:
            try:
                self.sg.connect(self.experimentParameters['sg_ip'])
                self.isSignalGeneratorConnected = True
                self.sgConnectButton.setText("Disconnect")
            except Exception as e:
                self.isSignalGeneratorConnected = False
                self.error(str(e), "Error signal generator")
                self.sgConnectButton.setText("Connect")


        else:
            self.sg.disconnect()
            self.isSignalGeneratorConnected = False
            self.sgConnectButton.setText("Connect")

    def selectSignalFile(self):
        """
         Loads the signal from a CSV file.

         """
        log.debug("Selecting signal file")
        def setFile(filePath):
            self.signalPath = filePath
            self.signal = np.loadtxt(filePath, dtype=np.uint16, delimiter=",")
            if len(self.signal.shape) == 1:
                self.signalPlot.plot(self.signal)
                self.sgFilePathEdit.setText(filePath)
            else:
                self.error("Error opening signal file, wrong format", "Signal file error")
                log.error("Error opening signal file, wrong format")

        #dialog = QFileDialog("Select the signal file.")
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.fileSelected.connect(setFile)
        if dialog.exec_():
            log.debug(f'Signal file selected')

    def sendSignalToSignalGenerator(self):
        """
        Action to send the signal to the signal generator.

        """
        if self.isSignalGeneratorConnected:
            try:
                log.debug(self.sgARBSelector.value())
                self.sg.setArbitraryWaveform(self.signal, register=self.sgARBSelector.value(), name="PIEZO_1")
            except Exception as e:
                errorMsg = f'An error occured during the setting of the signal: {str(e)}'
                log.error(errorMsg)
                self.error(errorMsg, "Error sending signal")
        else:
            self.error("The signal generator is not connected.", "Signal generator not connected")
            log.warning("The signal generator is not connected. Cannot send the signal.")

    def createSignalPlot(self):
        """
         Creates the plot widget but does not draw anything.

         """

        self.signalPlot = SG.SignalPlot(self.centralwidget)
        self.signalGeneratorLayout.addWidget(self.signalPlot)


################################################################################
#
# Setup the CNC.
#
################################################################################

    def connectCNC(self, args):
        """
         Connect to the CNC and set the status callback for the UI.

         """
        def cncStatusCallback(state, x, y, z):
            self.machineCoordinatesEdit.setText(f'{state},{x},{y},{z}')


        if self.isCncConnected == False:
            try:
                self.cnc.connect(self.experimentParameters['cnc_port'])
                self.cnc.start()
                self.isCncConnected = True
                self.connectCNCButton.setText("Disconnect")
                self.cnc.updateStatusCallback(cncStatusCallback)

                self.homeButton.setEnabled(True)
                self.stepEdit.setEnabled(True)
                self.positiveXButton.setEnabled(True)
                self.negativeXButton.setEnabled(True)
                self.positiveYButton.setEnabled(True)
                self.negativeYButton.setEnabled(True)
                self.positiveZButton.setEnabled(True)
                self.negativeZButton.setEnabled(True)
                self.unlockButton.setEnabled(True)
                self.zeroWorkingCoordinatesButton.setEnabled(True)
                self.goToWorkingZeroButton.setEnabled(True)
            except Exception as e:
                self.cncStarted = False
                self.error(str(e), "Error CNC")
            finally:
                pass
        else:
            self.cnc.stop()
            self.cnc.join()
            self.cnc = CNC.Cnc()
            self.isCncConnected = False
            self.connectCNCButton.setText("Connect")

            self.homeButton.setEnabled(False)
            self.stepEdit.setEnabled(False)
            self.positiveXButton.setEnabled(False)
            self.negativeXButton.setEnabled(False)
            self.positiveYButton.setEnabled(False)
            self.negativeYButton.setEnabled(False)
            self.positiveZButton.setEnabled(False)
            self.negativeZButton.setEnabled(False)
            self.unlockButton.setEnabled(False)
            self.zeroWorkingCoordinatesButton.setEnabled(False)
            self.goToWorkingZeroButton.setEnabled(False)

################################################################################
#
# Setup the experiment.
#
################################################################################

    def updateExpParams(self):
        """
        Update the exeriment parameters from the UI.

        """
        try:
            self.experimentParameters = ExpParamIO.toExpParamsFromJSON(self.jsonFormatParameters.toPlainText())
            self.oscilloscopeIPEdit.setText(self.experimentParameters['osc_ip'])
            self.sgSerialPortEdit.setText(self.experimentParameters['sg_ip'])
            self.portCNCEdit.setText(self.experimentParameters['cnc_port'])
        except json.JSONDecodeError as e:
            log.error(str(e))

    def setExperimentParameters(self,ep):
        """
        Set the experiment parameters.

        :param ep: The experiment parameters
        :type ep: dict

        """
        self.experimentParameters = ep
        self.jsonFormatParameters.setPlainText(ExpParamIO.toJSONFromExpParams(self.experimentParameters))

    def selectExperimentFile(self):
        """
         Loads experiment parameters from a file containing the parameters of a previous experiment.

         """
        log.debug("Selecting file")
        def setFile(filePath):
            self.jsonFormatParameters.textChanged.disconnect()
            self.experimentFile = filePath
            try:
                self.setExperimentParameters(ExpParamIO.readParametersFromFile(filePath))
            except Exception as e:
                log.error("Error opening experiment file", str(e))
            self.jsonFormatParameters.textChanged.connect(self.updateExpParams)

        #dialog = QFileDialog("Select the signal file.")
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.fileSelected.connect(setFile)
        if dialog.exec_():
            log.debug(f'File selected : {self.experimentFile}')

    def saveExperimentFile(self):
        """
         Save experiment parameters to a file containing the parameters.

         """
        log.debug("Saving file")

        try:
            self.experimentFile
        except AttributeError:
            self.experimentFile = None

        if self.experimentFile == None:
            try:
                ExpParamIO.writeParametersToFile("experiment_parameters.json", self.experimentParameters)
            except Exception as e:
                log.error("Error opening experiment file", e)
        else:
            try:
                ExpParamIO.writeParametersToFile(self.experimentFile, self.experimentParameters)
            except Exception as e:
                log.error("Error opening experiment file", e)

    def startMeasuring(self):
        """
         Launches the measurement process.

         """
        if self.isCncConnected and self.isSignalGeneratorConnected and self.isOscilloscopeConnected:
            scanner = mv.SurfaceVibrationsScanner(self.cnc, self.osc, self.sg, self.experimentParameters)
            rawData = scanner.startScanning()

            self.data = MeasureDataset.MeasureDataset(rawData, experimentParameters=self.experimentParameters)
            self.data.save_to(self.experimentParameters['data_filename'])
        else:
            self.error("Connect all the instruments before launching the experiment", "Unable to start")


################################################################################
#
# PLOT MANAGEMENT
#
################################################################################

    def createPlot(self):
        """
         Creates the plot widget but does not draw anything.

         """

        self.mainPlot = mainPlot.MainPlot(self.centralwidget)
        self.plotLayout.addWidget(self.mainPlot)

    def initPlot(self):
        """
         Initializes and draw the main plot.

         """
        self.mainPlot.init_plot(self.data)
        self.saveAnimationButton.clicked.connect(self.mainPlot.save_animation)

    def update_plot_in_time(self, fraction):
        """
         Changes the time of the plot and redraw it.

         """
        self.mainPlot.update_plot(time=fraction)
        time = self.data.get_time_scale()*fraction/1000
        self.timeEdit.setText(f'{time} s')

    def update_plot_limits(self):
        """
            Update the plot update limits.
        """
        upString = self.maxZLineEdit.text()
        downString = self.minZLineEdit.text()

        if Gui.is_number(upString) and Gui.is_number(downString):
            self.mainPlot.setZLimits(float(upString), float(downString))
        else:
            self.error("This Z limit is not a number. Please, change it.", "Z limit NAN")


    def selectDataFile(self):
        """
         Loads data from a datafile containing the data of a previous experiment.

         """
        log.debug("Selecting file")
        def setFile(filePath):
            self.dataFile = filePath
            try:
                self.data = MeasureDataset.MeasureDataset.load_from(filePath)
                self.initPlot()
            except Exception as e:
                log.error("Error opening data file: " + str(e))


        #dialog = QFileDialog("Select the signal file.")
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.fileSelected.connect(setFile)
        if dialog.exec_():
            log.debug(f'File selected : {self.dataFile}')

    def save_main_plot(self):
        """
        Save the main plot to the specified file (in the UI).

        """
        file = self.pathFigureLineEdit.text()
        try:
            self.mainPlot.saveFigure(file)
        except Exception as e:
            self.error(str(e), "Error saving figure")

################################################################################
#
# Close everything
#
################################################################################

    def closeEvent(self, args):
        self.closeRessources()

    def __del__(self):
        self.closeRessources()

    def closeRessources(self):
        """
        Free all the ressources.

        """
        log.debug("Trying to close ressources")
        try:
            self.cnc.stop()
            #self.cnc.join()
            self.sg.disconnect()
            self.osc.disconnect()
        except Exception as e:
            log.error("Problem freeing resources")
        finally:
            pass

################################################################################
#
# Error management
#
################################################################################

    def error(self, message, title="Error"):
        """
        Generate an error dialog.

        :param message: Message to display in the dialog
        :type message: string
        :param title: Title of the dialog
        :type title: string

        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)

        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def is_number(s):
        """
        Test if an object is a number.

        :param s: object to test
        :type s: object

        :return: Boolean indicating if the object is a numbe
        :rtype: boolean

        """
        try:
            float(s)
            return True
        except ValueError:
            return False
