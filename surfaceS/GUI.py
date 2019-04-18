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
# GUI.py


"""

from PyQt5.QtWidgets import (QApplication, QMainWindow, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

import sys
import logging as log
import json
import pandas as pd

from ui.mainwindow import Ui_MainWindow as MainWindow

import Oscilloscope as Osc
import SignalGenerator as SG
import cnc as CNC
import measure_vibrations as mv

class Gui(QMainWindow, MainWindow):
    def __init__(self, parent=None):
        super(Gui, self).__init__(parent)
        log.debug('Preparing GUI...')
        self.setupUi(self)

        self.experimentParameters = {}
        self.setDefaultExperimentParameters()

        def updateJSONFromExpParams():
            self.jsonFormatParameters.setPlainText(json.dumps(self.experimentParameters, indent=4))

        def updateExpParamsFromJSON():
            try:
                self.experimentParameters = json.loads(self.jsonFormatParameters.toPlainText())
            except json.JSONDecodeError as e:
                log.error(e.msg)

        self.jsonFormatParameters.selectionChanged.connect(updateJSONFromExpParams)
        self.jsonFormatParameters.textChanged.connect(updateExpParamsFromJSON)
        self.cncStarted = False

        log.debug('GUI ready')

        self.sg = SG.SignalGenerator()
        self.osc = Osc.Oscilloscope()
        self.cnc = CNC.Cnc()

        self.connectCNCButton.clicked.connect(self.connectCNC)
        self.homeButton.clicked.connect(self.cnc.home)
        self.cnc_step = 1

        def setCncStep():
            self.cnc_step = float(self.stepEdit.text())

        self.stepEdit.textChanged.connect(setCncStep)

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

        self.positiveXButton.clicked.connect(jogXPlus)
        self.negativeXButton.clicked.connect(jogXMinus)
        self.positiveYButton.clicked.connect(jogYPlus)
        self.negativeYButton.clicked.connect(jogYMinus)
        self.positiveZButton.clicked.connect(jogZPlus)
        self.negativeZButton.clicked.connect(jogZMinus)

        self.zeroWorkingCoordinatesButton.clicked.connect(self.cnc.zeroWorkingCoordinates)

        def goToZeroCNC():
            self.cnc.goToWorking(0,0,0)

        self.goToWorkingZeroButton.clicked.connect(goToZeroCNC)

        def setStartCoordinates():
            (x, y, z) = self.cnc.getMachineCoordinates()
            self.startMachineCoordinatesEdit.setText(f'{x},{y},{z}')
            self.experimentParameters['start_x'] = x
            self.experimentParameters['start_y'] = y
            self.experimentParameters['start_z'] = z
        self.setStartCoordinatesButton.clicked.connect(setStartCoordinates)

        self.unlockButton.clicked.connect(self.cnc.unlock)

        self.startMeasuringButton.clicked.connect(self.startMeasuring)

        self.osc.connect(self.experimentParameters['osc_ip'])
        self.sg.connect(self.experimentParameters['sg_port'])

        self.destroyed.connect(self.closeRessources)

    def connectCNC(self, args):
        def cncStatusCallback(state, x, y, z):
            self.machineCoordinatesEdit.setText(f'{state},{x},{y},{z}')


        if self.cncStarted:
            self.cnc.stop()
            self.cncStarted = False
        port = self.portCNCEdit.text()
        self.experimentParameters['cnc_port'] = port
        self.cnc.connect(port)
        if self.cncStarted == False:
            self.cnc.start()
            self.cncStarted = True
            self.cnc.updateStatusCallback(cncStatusCallback)

    def __del__(self):
        self.closeRessources()

    def closeRessources(self):
        log.debug("Trying to close ressources")
        self.cnc.stop()
        self.sg.disconnect()
        self.osc.disconnect()

    def setDefaultExperimentParameters(self):
        self.experimentParameters['cnc_port'] = "COM5"
        self.experimentParameters['start_x'] = -270.0
        self.experimentParameters['start_y'] = -232.0
        self.experimentParameters['start_z'] = -2.003
        self.experimentParameters['nb_point_x'] = 2
        self.experimentParameters['nb_point_y'] = 2
        self.experimentParameters['step_x'] = 10.0
        self.experimentParameters['step_y'] = 10.0
        self.experimentParameters['sg_port'] = "COM6"
        self.experimentParameters['wave_type'] = "SINE"
        self.experimentParameters['frequency'] = 10000
        self.experimentParameters['channel_sg'] = 1
        self.experimentParameters['osc_ip'] = "128.178.201.9"
        self.experimentParameters['vibrometer_channel'] = 2
        self.experimentParameters['reference_channel'] = 1
        self.experimentParameters['unit_time_division'] = "MS"
        self.experimentParameters['unit_volt_division'] = "MV"
        self.experimentParameters['volt_division_vibrometer'] = 20
        self.experimentParameters['volt_division_reference'] = 500
        self.experimentParameters['time_division'] = 5
        self.experimentParameters['trigger_level'] = 100
        self.experimentParameters['trigger_mode'] = "SINGLE"
        self.experimentParameters['trigger_delay'] = 0

    def closeEvent(self, args):
        self.closeRessources()

    def startMeasuring(self):
        scanner = mv.SurfaceVibrationsScanner(self.cnc, self.osc, self.sg, self.experimentParameters)
        self.data = pd.DataFrame()
        self.data = scanner.startScanning()

        #self.data.to_csv("data1.csv")
