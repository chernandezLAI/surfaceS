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
 *Last modification:* 09.05.2019

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

import MeasureDataset

Z_LIM_UP_DEFAULT = 50
Z_LIM_DOWN_DEFAULT = -50

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

        self.zLimDown = Z_LIM_DOWN_DEFAULT
        self.zLimUp = Z_LIM_UP_DEFAULT

    def init_plot(self, data, type="3D_MAP", args={}):
        self.type = type
        self.dataset = data
        self.data = data.get_data()

        self.datalength = self.data.shape[0]

        if type=="3D_MAP":
            self.ax = self.fig.gca(projection='3d')

            tmpHead = self.data.columns
            self.x = np.empty(tmpHead.size)
            self.y = np.empty(tmpHead.size)
            for i in range(1,tmpHead.size):
                coord = tmpHead[i].split(",")
                try:
                    self.x[i-1] = float(coord[0])
                    self.y[i-1] = float(coord[1])
                except Exception as e:
                    self.x[i-1] = 0.0
                    self.y[i-1] = 0.0
                    log.warning(f'Problem converting coordinates, {str(e)}')
                #z[i-1] = data.iloc[t,i-1]

            self.listX = np.unique(self.x)
            self.listY = np.unique(self.y)
            self.listX = np.delete(self.listX, self.listX.size-1)
            self.listY = np.delete(self.listY, self.listY.size-1)

            self.z = np.empty((self.listX.size,self.listY.size))

            log.debug(f'size listX = {self.listX.shape}, size listY = {self.listY.shape}')
        elif self.type=="2D_signal":
            pass

        self.ready = True
        self.update_plot(0)

    def update_plot(self, time=0, totalTime=1000):
        if self.ready == False:
            return
        t = time*int(self.data.shape[0] / totalTime)
        log.debug(f't={t}')

        self.ax.clear()

        i = 0
        for uX in self.listX:
            tt = np.where(self.x==uX)
            j = 0
            for uY in self.listY:
                tz = np.where(self.y==uY)
                zidx = self.findCoincidentIdx(tt[0], tz[0])
                if zidx >= 0:
                    #log.debug(f'Registering...')
                    self.z[i][j] = self.data.iloc[t,zidx+1]*self.dataset.zScale
                else:
                    self.z[i][j] = 0
                j = j+1
            i = i+1

        pX, pY = np.meshgrid(self.listX,self.listY, indexing='ij')

        log.debug(f'size pX = {pX.size}, size pY = {pY.size}, shape z ={self.z.shape}')
        #log.debug(f'shape z ={self.z.shape}')

        #print(self.z)
       # print(pX)
        #print(pY)
        #print(self.listX)
        #print(self.listY)

        # Plot the surface.
        self.surf = self.ax.plot_surface(pX, pY, self.z, cmap=cm.coolwarm, linewidth=0, antialiased=True)
        #self.surf = self.ax.plot_surface(self.listX, self.listY, self.z, cmap=cm.coolwarm, linewidth=0, antialiased=True)
        self.ax.set_zlabel('Amplitude in $\mu m$')

        # diff = self.zLimUp-self.zLimDown
        # if diff < 255:
        #     self.zLimUp = self.zLimDown + diff/2
        #     self.zLimDown = self.zLimDown + diff/2
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

    def setZLimits(self, up=Z_LIM_UP_DEFAULT, down=Z_LIM_DOWN_DEFAULT):
        self.zLimDown = down
        self.zLimUp = up
        if self.ready:
            self.ax.set_zlim(self.zLimDown, self.zLimUp)
            self.draw()

    def saveFigure(self, filename, dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None, metadata=None):
        self.fig.savefig(filename, dpi=None, facecolor='w', edgecolor='w',
        orientation='portrait', papertype=None, format=None,
        transparent=False, bbox_inches=None, pad_inches=0.1,
        frameon=None, metadata=None)

    def save_animation(self):

        #numberOfFrame = self.data.shape[0]
        numberOfFrame = 50000
        jumpSize = 16

        fig = Figure(figsize=(8, 8), dpi=150)
        ax = fig.gca(projection='3d')

        self.canvas = FigureCanvas(fig)

        tmpHead = self.data.columns
        self.animX = np.empty(tmpHead.size)
        self.animY = np.empty(tmpHead.size)
        self.animListX = []
        self.animListY = []

        self.animZ = []

        def init_anim():
            for i in range(1,tmpHead.size):
                coord = tmpHead[i].split(",")
                try:
                    self.animX[i-1] = float(coord[0])
                    self.animY[i-1] = float(coord[1])
                except Exception as e:
                    self.animX[i-1] = 0.0
                    self.animY[i-1] = 0.0
                    log.warning(f'Problem converting coordinates, {str(e)}')
                #z[i-1] = data.iloc[t,i-1]

            self.animListX = np.unique(self.animX)
            self.animListY = np.unique(self.animY)
            self.animListX = np.delete(self.animListX, self.animListX.size-1)
            self.animListY = np.delete(self.animListY, self.animListY.size-1)

            self.animZ = np.empty((self.animListX.size,self.animListY.size))
            return iterate_anim(1)

        def iterate_anim(frame):
            t = jumpSize*frame+38880
            log.debug(f't={t}/{numberOfFrame}')

            time = self.dataset.get_time_scale()*t/numberOfFrame

            ax.clear()

            i = 0
            # try:
            #     if(listX == None):
            #         return
            # except Exception as e:
            #     log.warning(str(e))

            for uX in self.animListX:
                tt = np.where(self.animX==uX)
                j = 0
                for uY in self.animListY:
                    tz = np.where(self.animY==uY)
                    zidx = self.findCoincidentIdx(tt[0], tz[0])
                    if zidx >= 0:
                        #log.debug(f'Registering...')
                        self.animZ[i][j] = self.data.iloc[t,zidx+1]*self.dataset.zScale
                    else:
                        self.animZ[i][j] = 0
                    j = j+1
                i = i+1

            pX, pY = np.meshgrid(self.animListX,self.animListY, indexing='ij')

            # Plot the surface.
            surf = ax.plot_surface(pX, pY, self.animZ, cmap=cm.coolwarm, linewidth=0, antialiased=True)
            ax.set_zlabel('Amplitude in $\mu m$')
            fig.suptitle('time: {:03.3f} $\mu s$'.format(1000000.0*time))
            ax.set_zlim(self.zLimDown, self.zLimUp)

            return surf,

        ani = animation.FuncAnimation(fig, iterate_anim, init_func=init_anim, interval=10, blit=True, save_count=int(numberOfFrame/jumpSize))

        plt.show()

        from matplotlib.animation import FFMpegWriter
        writer = FFMpegWriter(fps=60, metadata=dict(artist='Jérémy Jayet'), bitrate=1800)
        ani.save("animated_plot_FINAL_4.mp4", writer=writer)

        #ani.save("animated_plot_FINAL_2.mp4")


    def filter_lp():
        pass
