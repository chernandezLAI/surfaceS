

from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget, QFileDialog)

import logging as log

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from scipy.io import wavfile

class SignalGeneratorWidget(QVBoxLayout):
    def __init__(self, parent=None):
        super(SignalGeneratorWidget, self).__init__(parent)

        self.createFilePathView()
        self.createLoadButton()
        self.createSelFileButton()

        loaderLayout = QHBoxLayout()
        loaderLayout.addWidget(self.mLoadButton)
        loaderLayout.addWidget(self.mSelFileButton)
        loaderLayout.addWidget(self.mFilePathView)
        self.addLayout(loaderLayout)

        # a figure instance to plot on
        self.mSignalPlot = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.mSignalCanvas = FigureCanvas(self.mSignalPlot)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        #self.mSignalToolbar = NavigationToolbar(self.mSignalCanvas, self)

        # set the layout
        signalLayout = QVBoxLayout()
        #signalLayout.addWidget(self.mSignalToolbar)
        signalLayout.addWidget(self.mSignalCanvas)
        self.addLayout(signalLayout)

    def createFilePathView(self):
        self.mFilePathView = QLineEdit()
        self.mFilePathView.setReadOnly(True);

    def createLoadButton(self):
        self.mLoadButton = QPushButton("Load")
        self.mLoadButton.clicked.connect(self.load)

    def load(self):
        samplerate, data = wavfile.read(self.mFilePath)

        # create an axis
        ax = self.mSignalPlot.add_subplot(111)

        # discards the old graph
        ax.clear()

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.mSignalCanvas.draw()

    def createSelFileButton(self):
        self.mSelFileButton = QPushButton("Select file")
        self.mSelFileButton.clicked.connect(self.selectFile)

    def selectFile(self):
        log.debug("Selecting file")
        def setFile(filePath):
            self.mFilePath = filePath
            self.mFilePathView.setText(filePath)


        #dialog = QFileDialog("Select the signal file.")
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.fileSelected.connect(setFile)
        if dialog.exec_():
            log.debug(f'File selected : {self.mFilePath}')
