# Imports
from surfaceS import Oscilloscope as Osc
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Variables and objects
data = pd.DataFrame()
osc = Osc.Oscilloscope()

# Connect Oscillo
osc.connect(ip="128.178.201.12")
osc.printID()

# Set Oscillo for single Acquisition
osc.setGrid(10,2500,1,'MV','MS')            # time_division, volt_division_reference, reference_channel, unit_volt_division, unit_time_division
osc.setGrid(10,5000,2,'MV','MS')            # time_division, volt_division_vibrometer, vibrometer_channel, unit_volt_division, unit_time_division
osc.setTrigger(2500, -0.05, 1, "SINGLE", 'MV')  # trigger_level, trigger_delay, reference_channel, trigger_mode, unit_volt_division

# Acquire and plot data
tmpData = osc.acquire(readOnly=True, channel=2)

plt.subplot(1,2,1)
plt.plot(tmpData["data"])

fftData = np.fft.fft(data["data"])
plt.subplot(1,2,2)
plt.plot(fftData)

plt.show()

# Disconnect Oscillo
osc.disconnect()
