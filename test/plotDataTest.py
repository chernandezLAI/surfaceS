import unittest

import sys
import time
import logging as log
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# This import registers the 3D projection, but is otherwise unused.
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused impor
from matplotlib import cm
import matplotlib.animation as animation

if sys.platform.startswith('win32'):
    sys.path.append("C:\\Users\\jjayet\\Desktop\\SEM-PROJ_CNC_scanning\\surfaceS")
elif sys.platform.startswith('linux'):
    sys.path.append("~/EPFL/Cours/MA2/SEM-PROJ_CNC_scanning/surfaceS")
    log.debug("linux system")

class TestOscilloscope(unittest.TestCase):
    """
    Our basic test class
    """

    def test_plot(self):
        def findCoincidentIdx(tt, tz):
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

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        data = pd.read_csv("data_2019_04_18.csv")

        tmpHead = data.columns
        x = np.empty(tmpHead.size)
        y = np.empty(tmpHead.size)
        for i in range(1,tmpHead.size):
            coord = tmpHead[i].split(",")
            x[i-1] = float(coord[0])
            y[i-1] = float(coord[1])
            #z[i-1] = data.iloc[t,i-1]

        listX = np.unique(x)
        listY = np.unique(y)
        listX = np.delete(listX, listX.size-1)
        listY = np.delete(listY, listY.size-1)
        #listX = np.delete(listX, 0)
        #listY = np.delete(listY, 0)
        #print(listX)
        #print(listY)

        z = np.empty((listX.size,listY.size))

        def update_plot(frame, data, listX, listY):
            t = 10*frame
            print("t=",t)

            i = 0
            for uX in listX:
                tt = np.where(x==uX)
                j = 0
                for uY in listY:
                    tz = np.where(y==uY)
                    #print(tt)
                    #print(tz)
                    zidx = findCoincidentIdx(tt[0], tz[0])
                    #zidx = np.where(tt[0]==tz[0])
                    #print("zidx = ", zidx)
                    if zidx >= 0:
                        z[i][j] = data.iloc[t,zidx+1]
                    else:
                        z[i][j] = 0
                    j = j+1
                i = i+1

            #print(z)

            listX, listY = np.meshgrid(listX,listY)

            # Plot the surface.
            surf = ax.plot_surface(listX, listY, z, cmap=cm.coolwarm, linewidth=0, antialiased=True)

            ax.set_zlim(-300, 10000)

        anim = animation.FuncAnimation(fig, update_plot, frames=500, fargs=(data, listX, listY))

        plt.show()

if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    unittest.main()
