
from PyQt5.QtWidgets import (QApplication, QMainWindow, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit,
        QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QWidget)

from SignalGeneratorWidget import SignalGeneratorWidget as signalW


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        #self.mMainWindow = QMainWindow()

        self.mCentralWidget = QWidget()

        self.mSignalGeneratorWidget = signalW()

        self.mCentralWidget.setLayout(self.mSignalGeneratorWidget)

        self.setCentralWidget(self.mCentralWidget)

        self.show()

#    def initSignalGeneratorWidget(self, parent=None):
