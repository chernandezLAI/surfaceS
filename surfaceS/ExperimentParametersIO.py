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
 The ``GUI`` module
 ======================

 *Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
 *Last modification:* 02.05.2019

 This module implements the different features of the GUI. The layout itself is
 described in the [mainwindow.ui](ui/mainwindow.ui) file.

 """

import json
import logging as log

def getDefaultParameters():
    """
     Prepare the default values for the experiment.
     """
    experimentParameters = {}
    experimentParameters['cnc_port'] = "COM5"
    experimentParameters['start_x'] = -270.0
    experimentParameters['start_y'] = -232.0
    experimentParameters['start_z'] = -2.003
    experimentParameters['nb_point_x'] = 2
    experimentParameters['nb_point_y'] = 2
    experimentParameters['step_x'] = 10.0
    experimentParameters['step_y'] = 10.0
    experimentParameters['sg_port'] = "COM6"
    experimentParameters['wave_type'] = "SINE"
    experimentParameters['frequency'] = 10000
    experimentParameters['channel_sg'] = 1
    experimentParameters['osc_ip'] = "128.178.201.9"
    experimentParameters['vibrometer_channel'] = 2
    experimentParameters['reference_channel'] = 1
    experimentParameters['unit_time_division'] = "MS"
    experimentParameters['unit_volt_division'] = "MV"
    experimentParameters['volt_division_vibrometer'] = 20
    experimentParameters['volt_division_reference'] = 500
    experimentParameters['time_division'] = 5
    experimentParameters['trigger_level'] = 100
    experimentParameters['trigger_mode'] = "SINGLE"
    experimentParameters['trigger_delay'] = 0
    experimentParameters['data_filename'] = "data.csv"

    return experimentParameters

def toJSONFromExpParams(experimentParameters):
    return json.dumps(experimentParameters, indent=4)

def toExpParamsFromJSON(jsonInput):
    try:
        experimentParameters = json.loads(jsonInput)
        return experimentParameters
    except Exception as e:
        log.error(str(e))
        return getDefaultParameters()

def readParametersFromFile(filename="experiment_parameters.json"):
    fhandle = open(filename)
    param = json.load(fhandle)
    fhandle.close()
    return param
def writeParametersToFile(filename, parameters):
    try:
        fhandle = open(filename, "w")
        fhandle.write(toJSONFromExpParams(parameters))
        fhandle.close()
    except Exception as e :
        log.error(str(e))
        return getDefaultParameters()
