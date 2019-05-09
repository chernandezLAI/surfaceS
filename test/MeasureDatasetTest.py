import unittest

import sys
import time
import logging as log
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

if sys.platform.startswith('win32'):
    sys.path.append("C:\\Users\\jjayet\\Desktop\\SEM-PROJ_CNC_scanning\\surfaceS")
elif sys.platform.startswith('linux'):
    sys.path.append("~/EPFL/Cours/MA2/SEM-PROJ_CNC_scanning/surfaceS")
    log.debug("linux system")


from surfaceS import MeasureDataset

class TestMeasureDataset(unittest.TestCase):
    """
    Our basic test class
    """

    def test_to_json(self):
        md = MeasureDataset.MeasureDataset(data=pd.read_csv("2019_05_09_data_SQUARE7.csv"))
        md2 = MeasureDataset.MeasureDataset()
        a = md.to_json()
        md2.from_json(a)
        #print(md2.to_json())
        assert(strcmp(a,md2.to_json()))

    def test_to_file(self):
        md = MeasureDataset.MeasureDataset(data=pd.read_csv("2019_05_09_data_SQUARE7.csv"))
        md.save_to("Test_file.json")
    def test_from_file(self):
        md = MeasureDataset.MeasureDataset.load_from("Test_file.json")


if __name__ == '__main__':
    log.basicConfig(level=log.DEBUG)
    unittest.main()
