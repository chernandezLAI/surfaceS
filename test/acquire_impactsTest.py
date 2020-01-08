import Oscilloscope as Osc
import SignalGeneratorTCPIP as SG
import cnc as CNC
import acquire_impacts as av
import ExperimentParametersIO as ExpParamIO

isOscilloscopeConnected = False
isCncConnected = False
isSignalGeneratorConnected = False

sg = SG.SignalGeneratorTCPIP()
osc = Osc.Oscilloscope()
cnc = CNC.Cnc()

experimentParameters = {}
# experimentParameters = ExpParamIO.getDefaultParameters()

experimentParameters['cnc_port'] = "COM10"
experimentParameters['delay_before_measuring'] = 0.2
experimentParameters['start_x'] = -270.0
experimentParameters['start_y'] = -232.0
experimentParameters['start_z'] = -2.003
experimentParameters['nb_point_x'] = 2
experimentParameters['nb_point_y'] = 2
experimentParameters['step_x'] = 10.0
experimentParameters['step_y'] = 10.0

experimentParameters['sg_port'] = "COM6"
experimentParameters['sg_ip'] = "128.178.201.37"
experimentParameters['wave_type'] = "SINE"
experimentParameters['frequency'] = 10000
experimentParameters['channel_sg'] = 1

experimentParameters['osc_ip'] = "128.178.201.12"
experimentParameters['vibrometer_channel'] = 2
experimentParameters['reference_channel'] = 1
experimentParameters['unit_time_division'] = "MS"
experimentParameters['unit_volt_division'] = "MV"
experimentParameters['volt_division_vibrometer'] = 20
experimentParameters['volt_division_reference'] = 500
experimentParameters['time_division'] = 0.05
experimentParameters['trigger_level'] = 100
experimentParameters['trigger_mode'] = "SINGLE"
experimentParameters['trigger_delay'] = 0
experimentParameters['data_filename'] = "data.csv"

cnc_step = 1

#%% CNC
cnc.connect(experimentParameters['cnc_port'])
cnc.start()
isCncConnected = True

#%% Oscilloscope
osc.connect(experimentParameters['osc_ip'])
isOscilloscopeConnected = True

#%% SignalGenerator
sg.connect(experimentParameters['sg_ip'])
isSignalGeneratorConnected = True
