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
 *Last modification:* 02.05.2019

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

from ui.mainwindow import Ui_MainWindow as MainWindow

import matplotlib as plt
# Make sure that we are using QT5
plt.use('Qt5Agg')

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import Oscilloscope as Osc
import SignalGenerator as SG
import cnc as CNC
import measure_vibrations as mv
import mainPlot
import ExperimentParametersIO as ExpParamIO

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

        self.experimentParameters = {}
        self.setExperimentParameters(ExpParamIO.getDefaultParameters())

        self.jsonFormatParameters.textChanged.connect(self.updateExpParams)

        self.sg = SG.SignalGenerator()
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
        self.setStartCoordinatesButton.clicked.connect(setStartCoordinates)

        self.startMeasuringButton.clicked.connect(self.startMeasuring)

        self.sgConnectButton.clicked.connect(self.connectSg)

        self.createPlot()

        self.actionOpenDataFile.triggered.connect(self.selectDataFile)

        self.actionOpenExperimentFile.triggered.connect(self.selectExperimentFile)

        self.actionSaveExperimentFile.triggered.connect(self.saveExperimentFile)

        self.timeSlider.valueChanged[int].connect(self.update_plot_in_time)

        self.connectOscilloscopeButton.clicked.connect(self.connectOsc)
        self.oscilloscopeIPEdit.setText(self.experimentParameters['osc_ip'])

        self.sgConnectButton.clicked.connect(self.connectSg)
        self.sgSerialPortEdit.setText(self.experimentParameters['sg_port'])

        #self.osc.connect(self.experimentParameters['osc_ip'])
        #self.sg.connect(self.experimentParameters['sg_port'])

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
                self.sg.connect(self.experimentParameters['sg_port'])
                self.isSignalGeneratorConnected = True
                self.sgConnectButton.setText("Disconnect")
            except Exception as e:
                self.cncStarted = False
                self.error(str(e), "Error signal generator")


        else:
            self.sg.disconnect()
            self.isSignalGeneratorConnected = False
            self.sgConnectButton.setText("Connect")

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
        try:
            self.experimentParameters = ExpParamIO.toExpParamsFromJSON(self.jsonFormatParameters.toPlainText())
        except json.JSONDecodeError as e:
            log.error(e.msg)

    def setExperimentParameters(self,ep):
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
         Launches the measurements
         """
        if self.isCncConnected and self.isSignalGeneratorConnected and self.isOscilloscopeConnected:
            scanner = mv.SurfaceVibrationsScanner(self.cnc, self.osc, self.sg, self.experimentParameters)
            self.data = scanner.startScanning()
            #self.data = scanner.startScanning()

            #self.initPlot()

            self.data.to_csv(self.experimentParameters['data_filename'])
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

    def update_plot_in_time(self, fraction):
        """
         Changes the time of the plot and redraw it.
         """
        self.mainPlot.update_plot(time=fraction)
        self.timeEdit.setText(f'{fraction} samples')


    def selectDataFile(self):
        """
         Loads data from a datafile containing the data of a previous experiment.
         """
        log.debug("Selecting file")
        def setFile(filePath):
            self.dataFile = filePath
            try:
                self.data = pd.read_csv(filePath)
                self.initPlot()
            except Exception as e:
                log.error("Error opening data file", e)


        #dialog = QFileDialog("Select the signal file.")
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.fileSelected.connect(setFile)
        if dialog.exec_():
            log.debug(f'File selected : {self.dataFile}')

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
        log.debug("Trying to close ressources")
        try:
            self.cnc.stop()
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
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)

        msg.setText(message)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
