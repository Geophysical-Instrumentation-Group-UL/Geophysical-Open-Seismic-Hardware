import unittest
import time
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.Qt import QPixmap
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QThreadPool, QThread
from PyQt5 import uic
import os
from gui.modules import mockSpectrometer as mock
from tools.threadWorker import Worker
from tools.CircularList import RingBuffer
import numpy as np
from numpy import trapz
import logging
import copy
import tools.sutterneeded.sutterdevice as phl
import seabreeze.spectrometers as sb

class TestMicroRamanView(unittest.TestCase):
    def testCanWeConnectDebugSutter(self):
        self.stageDevice = phl.SutterDevice(portPath="debug")


if __name__ == '__main__':
    unittest.main()