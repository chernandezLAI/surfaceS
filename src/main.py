

from PyQt5.QtWidgets import QApplication, QLabel

from GUI import MainWindow

import logging as log

if __debug__ :
    log.basicConfig(level=log.DEBUG)

log.debug('surfaceS started !')

app = QApplication([])

w = MainWindow()

app.exec_()
