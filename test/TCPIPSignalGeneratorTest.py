# %%
import visa
rm = visa.ResourceManager()
print(rm)
sg = rm.open_resource('TCPIP0::128.178.201.37::9221::SOCKET', read_termination='\n', write_termination = '\n')
sg.query('*IDN?')

#%%
sg.write('BEEP')
sg.write('CHN 1')
sg.write('WAVE PULSE')
sg.write('PULSFREQ 4')
sg.write('AMPUNIT VPP')
sg.write('AMPL 2.5')
sg.write('DCOFFS 1.25')
sg.write('PULSWID 0.04')
sg.write('PULSDLY 0')

sg.write('CHN 2')
sg.write('WAVE PULSE')
sg.write('PULSFREQ 4')
sg.write('AMPUNIT VPP')
sg.write('AMPL 2.5')
sg.write('DCOFFS 1.25')
sg.write('PULSWID 0.023')
sg.write('PULSDLY 0.104')
#sg.write('')
#sg.write('')

#%%

sg.close()
rm.close()
