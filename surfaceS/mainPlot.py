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
 The ``MainPlot`` module
 ======================

 *Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
 *Last modification:* 02.05.2019

 In this module, the main plot is created and managed.

 """

import logging as log
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused impor
from matplotlib import cm
import matplotlib.animation as animation

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

class MainPlot(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #self.ax = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        self.ready = False

        self.zLimDown = -16000
        self.zLimUp = -10000

    def init_plot(self, data, type="3D_MAP", args={}):
        self.ready = True
        self.type = type
        self.data = data

        # Automatic refreshing
        #timer = QtCore.QTimer(self)
        #timer.timeout.connect(self.update_plot)
        #timer.start(1000)

        if type=="3D_MAP":
            self.ax = self.fig.gca(projection='3d')

            tmpHead = self.data.columns
            self.x = np.empty(tmpHead.size)
            self.y = np.empty(tmpHead.size)
            for i in range(1,tmpHead.size):
                coord = tmpHead[i].split(",")
                self.x[i-1] = float(coord[0])
                self.y[i-1] = float(coord[1])
                #z[i-1] = data.iloc[t,i-1]

            self.listX = np.unique(self.x)
            self.listY = np.unique(self.y)
            self.listX = np.delete(self.listX, self.listX.size-1)
            self.listY = np.delete(self.listY, self.listY.size-1)

            self.z = np.empty((self.listX.size,self.listY.size))

            self.update_plot(0)

    def update_plot(self, time=0):
        if self.ready == False:
            return
        t = time
        print("t=",t)

        i = 0
        for uX in self.listX:
            tt = np.where(self.x==uX)
            j = 0
            for uY in self.listY:
                tz = np.where(self.y==uY)
                zidx = self.findCoincidentIdx(tt[0], tz[0])
                if zidx >= 0:
                    self.z[i][j] = self.data.iloc[t,zidx+1]
                else:
                    self.z[i][j] = 0
                j = j+1
            i = i+1

        #print(z)

        pX, pY = np.meshgrid(self.listX,self.listY)

        # Plot the surface.
        self.surf = self.ax.plot_surface(pX, pY, self.z, cmap=cm.coolwarm, linewidth=0, antialiased=True)
        self.zLimDown = np.amin(self.z)
        self.zLimUp = np.amax(self.z)
        diff = self.zLimUp-self.zLimDown
        if diff < 255:
            self.zLimUp = self.zLimDown + diff/2 + 128
            self.zLimDown = self.zLimDown + diff/2 - 128
        self.ax.set_zlim(self.zLimDown, self.zLimUp)
        self.draw()

    def findCoincidentIdx(self, tt, tz):
        w = 0
        for a in tt:
            for b in tz:
                #print("a = ", a, ", b = ", b)
                if a == b:
                    zidx = a
                    return zidx
                else:
                    w = w + 1
        return -1

        def setZLimits(up, down=self.zLimDown):
            self.zLimDown = down
            self.zLimUp = up
            self.ax.set_zlim(self.zLimDown, self.zLimUp)
            self.draw()
