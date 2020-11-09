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
 The ``MeasureDataset`` module
 =============================

 *Author:* [Jérémy Jayet](mailto:jeremy.jayet@epfl.ch)
 *Last modification:* 04.06.2019

 This module is a class to manage experiment data objects.
 The goal is to keep track of all the parameters even after the measurement to
 to be sure to keep all the metadata needed to interpret the data.

 """

import logging as log
import string
import numpy as np
import pandas as pd
from io import StringIO
import json
import re

import ExperimentParametersIO as ExpParamIO


VIBROMETER_HEIGHT_VOLTAGE = 0.001 # UNIT IN MICROMETER 1 um/V if voltage volt_division_vibrometer is V or 0.001 um/mV if voltage volt_division_vibrometer is MV   !!!

NUMBER_BIT_OSC_DATA = 16

MAX_VALUE_OSC_DATA = np.power(2, NUMBER_BIT_OSC_DATA)

NUMBER_VOLTAGE_DIVISION_OSC = 8

NUMBER_TIME_DIVISION_OSC = 10

TIME_UNIT_SCALE = 1000 # 1 if time unit_time_division is S or 1000 if if time unit_time_division is MS !!!

class MeasureDataset():
    def __init__(self, data=None, experimentParameters=ExpParamIO.getDefaultParameters()):
        self.experimentParameters = experimentParameters
        self.data = data

        self.numberOfSamples = self.data.shape[0]

        self.height_coefficient = 0

        #self.zScale = (NUMBER_VOLTAGE_DIVISION_OSC * self.experimentParameters['volt_division_vibrometer']*VIBROMETER_HEIGHT_VOLTAGE)/MAX_VALUE_OSC_DATA
        self.zScale = 3.90625e-06 # 3.90625e-06 Valid when Voltage division 30 mV / 0.0013020799932065218 Valid when Voltage division 10000 mV

        self.timeScale = (NUMBER_TIME_DIVISION_OSC*self.experimentParameters['time_division'])/(self.numberOfSamples*TIME_UNIT_SCALE)

    def set_data(self, data):
        """
        Set the data.

        :param data: The data to store in the MeasureDataset object.
        :type data: pd.Dataframe

        """
        self.data = data

    def get_data(self):
        """
        Get the data.

        :return: The data stored in the MeasureDataset object.
        :rtype: pd.Dataframe

        """
        return self.data

    def to_json(self):
        """
        Get the object in the form of a JSON string

        :return: The object serialized as a JSON string.
        :rtype: string

        """
        rootString = {}

        try:
            bufferCSV = StringIO()
            self.data.to_csv(bufferCSV)
            rootString['csv_data'] = bufferCSV.getvalue()
            bufferCSV.close()
        except Exception as e:
            log.error(str(e))

        metadata = {}

        metadata['height_coefficient'] = self.height_coefficient

        rootString['metadata'] = json.dumps(metadata, indent=4)

        rootString['experimentParameters'] = ExpParamIO.toJSONFromExpParams(self.experimentParameters)

        return json.dumps(rootString, indent=4)

    def from_json(self, inputJson):
        """
        Populate the object with a JSON string.

        :param inputJson: The JSON string
        :type inputJson: string

        """
        rootString = json.loads(inputJson)

        try:
            dataBuffer = StringIO(rootString['csv_data'])
            self.data = pd.read_csv(dataBuffer)
        except Exception as e:
            self.data = None
            log.error(str(e))

        metadata = json.loads(rootString['metadata'])

        self.height_coefficient = metadata['height_coefficient']

        self.experimentParameters = ExpParamIO.toExpParamsFromJSON(rootString['experimentParameters'])

    def save_to(self, filename):
        """
        Save the object as JSON in the specified file.

        :param filename: Path to the file
        :type filename: string

        """
        fhandle = open(filename, "w")
        fhandle.write(self.to_json())
        fhandle.close()

    def load_from(filename):
        """
        Creat an object from the specified JSON file.

        :param filename: Path to the file
        :type filename: string

        :return: The data object
        :rtype: MeasureDataset

        """
        filterJson =  re.compile('.json')
        filterCSV = re.compile('.csv')
        matchJson = filterJson.search(filename)
        matchCSV = filterCSV.search(filename)

        if matchJson != None:
            log.debug("Opening JSON file...")
            fhandle = open(filename)

            rootString = json.loads(fhandle.read())

            try:
                dataBuffer = StringIO(rootString['csv_data'])
                data = pd.read_csv(dataBuffer)
            except Exception as e:
                data = None
                log.error(str(e))

            parameters = ExpParamIO.toExpParamsFromJSON(rootString['experimentParameters'])

            fhandle.close()

            return MeasureDataset(data, parameters)
        elif matchCSV != None:
            log.debug("Opening CSV file...")
            data = pd.read_csv(filename)
            return MeasureDataset(data)
        else:
            raise NameError("The format is not supported.")

    def export_data_to(self, filename):
        pass

    def import_data_from(self, filename):
        pass

    def get_time_scale(self):
        return self.timeScale
