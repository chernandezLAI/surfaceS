import SignalGeneratorTCPIP as SG
import numpy as np

signalG = SG.SignalGeneratorTCPIP()
signalG.connect()
signalG.beep()
signalG.SetSineSweep_withTrigger(1000.0, 50000.0, 0.5, 1, 0.0)

signalG.setChannel(2)
signalG.setOutput(True)
signalG.setFrequency(200)
signalG.setWave("ARB", 3)
signalG.setWave("PULSE")
signalG.setBurstMode(1)
signalG.burst()
signalG.setChannel(2)
signalG.setAmplitude(2.5, "VPP",1.25)
signalG.setWave("PULSE")
signalG.setPulseFrequency(20)

signalG.setPulse(5.0, 2.5, "VPP", 1.25, 0.023, 0.104)
signalG.setTrigger("CRC")

signalG.setWave("ARB", 3) #OK --------------------
size = 1024
data = np.zeros(size, dtype=np.uint16)
for i in range(0, size-1):
    data[i] = 0.03*np.square(i)+0.01*i+1
signalG.setArbitraryWaveform(data, register=3, name="TEST3")

signalG.setTriggerSignal(1,0.0)

signalG.SetSineSweep_withTrigger(1000.0, 50000.0, 0.5, 1, 0.0)

signalG.disconnect()
# TO DEBUG THE BINARY VALUE Send

import visa
import numpy as np
import matplotlib.pyplot as plt


ip:str="128.178.201.37"
port:str="9221"

rm = visa.ResourceManager()
sg = rm.open_resource(f'TCPIP0::{ip}::{port}::SOCKET', read_termination='\n', write_termination = '\n')

sg.write("CHN 1")
sg.write("ARBLOAD ARB3")
sg.write("ARBDEF ARB3,TEST1,OFF")


size = 1024
data = np.zeros(size, dtype=np.uint16)
for i in range(0, size):
    data[i] = 0.03*np.square(i)+0.01*i+1

a=0
data = np.zeros(size, dtype=np.uint16)
for i in range(0, size):
    a = a + 1
    data[i] = a

plt.plot(data)
plt.show()

data = np.interp(data, (data.min(), data.max()), (0, 16383))
plt.plot(data)
plt.show()


header = "ARB" + str(3) + " "
size=data.size
sizeStr = str(2*size)
header = header + "#" + str(len(sizeStr)) + sizeStr

dataHandler = np.uint16()
bin = bytearray(header, 'utf-8')
for i in range(0, size-1):
     dataHandler = data[i]
     bytesToSend = int(dataHandler).to_bytes(2, byteorder='big', signed=False)
     bin.append(bytesToSend[0])
     bin.append(bytesToSend[1])

msg = bytes(bin)
sg.write_raw(msg)
sg.write('\n')
sg.write('BEEP')
