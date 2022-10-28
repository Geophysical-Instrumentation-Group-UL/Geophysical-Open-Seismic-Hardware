from PyQt5.QtCore import pyqtSignal, Qt, QThreadPool, QThread, QTimer
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.Qt import QPixmap
from PyQt5 import uic

import hardwarelibrary.communication.serialport as sepo
import hardwarelibrary.motion.sutterdevice as sutter
from tools.CircularList import RingBuffer
from tools.threadWorker import Worker

from gui.modules import mockSpectrometer as Mock
import seabreeze.spectrometers as sb

import matplotlib.pyplot as plt
import pyqtgraph as pg
import numpy as np
import logging
import copy
import os

log = logging.getLogger(__name__)


microRamanViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}microRamanViewUi.ui'.format(os.sep)
print(microRamanViewUiPath)
Ui_microRamanView, QtBaseClass = uic.loadUiType(microRamanViewUiPath)


class MicroRamanView(QWidget, Ui_microRamanView):  # type: QWidget
    s_data_changed = pyqtSignal(dict)
    s_data_acquisition_done = pyqtSignal()

    def __init__(self, model=None):
        super(MicroRamanView, self).__init__()
        self.setupUi(self)
        self.model = model

        self.direction = "other"
        self.folderPath = ""
        self.fileName = ""

        self.liveAcquisitionData = []
        self.backgroundData = []
        self.dataPixel = []

        self.integrationTimeAcqRemainder_ms = 0
        self.integrationTimeAcq = 3000
        self.countIntegrationWhile = 0
        self.changeLastExposition = 0
        self.acqTimeRemainder_ms = 0
        self.integrationCountAcq = 0
        self.expositionCounter = 0
        self.maxWaveLength = 255
        self.minWaveLength = 0
        self.exposureTime = 500
        self.countSpectrum = 0
        self.order = 10 ** 3
        self.countHeight = 0
        self.rangeLen = 255
        self.countWidth = 0
        self.dataSep = 0

        self.doSliderPositionAreInitialize = False
        self.launchIntegrationAcquisition = False
        self.isAcquisitionThreadAlive = False
        self.visualWithoutBackground = False
        self.isAcquiringIntegration = False
        self.isAcquiringBackground = False
        self.isBackgroundRemoved = False
        self.isSweepThreadAlive = False
        self.detectionConnected = False
        self.isAcquisitionDone = False
        self.isEveryAcqDone = False
        self.lightConnected = False
        self.stageConnected = False

        self.colorRangeViewEnable = True

        self.matrixDataWithoutBackground = None
        self.temporaryIntegrationData = None
        self.movingIntegrationData = None
        self.actualPosition = None
        self.mousePositionX = None
        self.mousePositionY = None
        self.positionSutter = None
        self.matrixRawData = None
        self.plotSpectrum = None
        self.stageDevice = None
        self.plotViewBox = None
        self.greenRange = None
        self.blueRange = None
        self.matrixRGB = None
        self.countSave = None
        self.plotItem = None
        self.redRange = None
        self.heightId = None
        self.widthId = None
        self.dataLen = None
        self.Height = None
        self.Width = None
        self.laser = None
        self.waves = None
        self.spec = None
        self.data = None
        self.img = None

        self.height = self.sb_height.value()
        self.width = self.sb_width.value()
        self.step = self.sb_step.value()
        self.threadpool = QThreadPool()
        self.sweepThread = QThread()
        self.update_slider_status()
        self.saveThread = QThread()
        self.initialize_buttons()
        self.connect_widgets()
        self.create_threads()

        self.lightDevices = ["None"]
        self.stageDevices = []  # sepo.SerialPort.matchPorts(idVendor=4930, idProduct=1)
        self.stageDevices.insert(0, "Debug")
        self.stageDevices.append("real sutter")
        self.listStageDevices = []
        for el in self.stageDevices:
            self.listStageDevices.append(str(el))
        self.specDevices = sb.list_devices()
        self.specDevices.insert(0, "MockSpectrometer")
        self.listSpecDevices = []
        for el in self.specDevices:
            self.listSpecDevices.append(str(el))
        self.cmb_selectDetection.addItems(self.listSpecDevices)
        self.cmb_selectLight.addItems(self.lightDevices)
        self.cmb_selectStage.addItems(self.listStageDevices)

    # Connect
    def connect_widgets(self):  # GUI
        self.cmb_magnitude.currentTextChanged.connect(self.set_measure_unit)
        self.dSlider_red.valueChanged.connect(self.set_red_range)
        self.dSlider_green.valueChanged.connect(self.set_green_range)
        self.dSlider_blue.valueChanged.connect(self.set_blue_range)
        self.graph_rgb.scene().sigMouseMoved.connect(self.mouse_moved)
        self.pb_background.clicked.connect(self.acquire_background)
        self.pb_saveData.clicked.connect(self.save_matrixRGB)
        self.pb_sweepSame.clicked.connect(lambda: setattr(self, 'direction', 'same'))
        self.pb_sweepAlternate.clicked.connect(lambda: setattr(self, 'direction', 'other'))
        self.pb_reset.clicked.connect(self.stop_acq)
        self.pb_liveView.clicked.connect(self.begin)
        self.pb_connectLight.clicked.connect(self.connect_light)
        self.pb_connectStage.clicked.connect(self.connect_stage)
        self.pb_connectDetection.clicked.connect(self.connect_detection)
        self.sb_height.textChanged.connect(lambda: setattr(self, 'height', self.sb_height.value()))
        self.sb_width.textChanged.connect(lambda: setattr(self, 'width', self.sb_width.value()))
        self.sb_step.textChanged.connect(lambda: setattr(self, 'step', self.sb_step.value()))

        self.sb_acqTime.valueChanged.connect(lambda: setattr(self, 'movingIntegrationData', None))
        self.sb_acqTime.valueChanged.connect(lambda: setattr(self, 'integrationTimeAcq', self.sb_acqTime.value()))
        self.sb_acqTime.valueChanged.connect(self.set_integration_time)

        self.sb_exposure.valueChanged.connect(lambda: setattr(self, 'exposureTime', self.sb_exposure.value()))
        self.sb_exposure.valueChanged.connect(self.set_exposure_time)
        self.tb_folderPath.clicked.connect(self.select_save_folder)

        self.sb_highRed.valueChanged.connect(self.update_slider_status)
        self.sb_lowRed.valueChanged.connect(self.update_slider_status)
        self.sb_highGreen.valueChanged.connect(self.update_slider_status)
        self.sb_lowGreen.valueChanged.connect(self.update_slider_status)
        self.sb_highBlue.valueChanged.connect(self.update_slider_status)
        self.sb_lowBlue.valueChanged.connect(self.update_slider_status)

        self.cmb_set_maximum.currentIndexChanged.connect(self.update_color)
        self.pb_saveImage.clicked.connect(self.save_image)
        self.cb_colorRangeView.stateChanged.connect(self.colorRangeView_status)

        self.cb_delete_background.stateChanged.connect(self.update_without_background)

        self.pb_save_without_background.clicked.connect(self.save_matrix_data_without_background)

        self.cmb_wave.currentIndexChanged.connect(self.set_wave)

    def set_wave(self):  # Controller
        if self.cmb_wave.currentIndex() == 0:
            self.waves = ((1 / self.laser) - (1 / self.spec.wavelengths()[2:])) * 10 ** 7
        if self.cmb_wave.currentIndex() == 1:
            self.waves = self.spec.wavelengths()[2:]
        self.dataSep = (max(self.waves) - min(self.waves)) / self.dataLen
        self.update_color()
        self.update_range_to_wave()
        self.update_slider_status()

    def update_without_background(self):  # Controller
        if not list(self.backgroundData):
            self.error_background()
            if self.cb_delete_background.checkState() == 2:
                QTimer.singleShot(1, lambda: self.cb_delete_background.setCheckState(0))

        else:
            self.create_matrix_data_without_background()
            if self.cb_delete_background.checkState() == 2:
                self.visualWithoutBackground = True
            if self.cb_delete_background.checkState() == 0:
                self.visualWithoutBackground = False
            self.update_color()

    def connect_light(self):  # On le garde tu? TODO
        log.debug("Initializing devices...")
        index = self.cmb_selectLight.currentIndex()
        if index == 0:
            # self.spec = Mock.MockSpectrometer()
            log.info("No light connected")
            self.lightConnected = False
        else:
            self.lightConnected = True

    def connect_stage(self):  # Model
        log.debug("Initializing devices...")
        index = self.cmb_selectStage.currentIndex()
        if index == 0:
            log.info("No stage connected; FakeStage Enabled.")
            self.stageDevice = sutter.SutterDevice(serialNumber="debug")
            self.stageDevice.doInitializeDevice()
            self.stageConnected = True
        else:
            # TODO will update with list provided by sepo.SerialPort.matchPorts(idVendor=4930, idProduct=1)...
            # self.stageDevice = None
            self.stageDevice = sutter.SutterDevice()
            self.stageDevice.doInitializeDevice()
            self.stageConnected = True
        if self.stageDevice is None:
            raise Exception('The sutter is not connected!')
        self.positionSutter = self.stageDevice.position()

    def connect_detection(self):  # Model
        if self.le_laser.text() == "":
            self.error_laser_wavelength()
        else:
            try:
                self.laser = int(self.le_laser.text())
                log.debug("Initializing devices...")
                index = self.cmb_selectDetection.currentIndex()
                if index == 0:
                    self.spec = Mock.MockSpectrometer()
                    log.info("No device connected; Mocking Spectrometer Enabled.")
                    self.detectionConnected = True
                else:
                    self.spec = sb.Spectrometer(self.specDevices[index])
                    log.info("Devices:{}".format(self.specDevices))
                    self.detectionConnected = True
                if self.cmb_wave.currentIndex() == 0:
                    self.waves = ((1 / self.laser) - (1 / self.spec.wavelengths()[2:])) * 10 ** 7
                if self.cmb_wave.currentIndex() == 1:
                    self.waves = self.spec.wavelengths()[2:]
                self.dataLen = len(self.waves)
                self.dataSep = (max(self.waves) - min(self.waves)) / self.dataLen
                self.cmb_wave.setEnabled(True)
                self.set_exposure_time()
                self.set_range_to_wave()
                self.update_slider_status()
                self.cmb_wave.setEnabled(True)
                # self.backgroundData = np.zeros(len(self.spec.wavelengths()[2:]))
            except:
                self.error_laser_wavelength()

    def mouse_moved(self, pos):  # GUI
        try:
            value = self.plotViewBox.mapSceneToView(pos)
            valueSTR = str(value)
            valueMin = valueSTR.find("(")
            valueMax = valueSTR.find(")")
            position = valueSTR[valueMin+1:valueMax]
            position = position.split(",")
            positionX = int(float(position[1]))
            positionY = int(float(position[0]))

            if positionX <= -1 or positionY <= -1:
                pass

            else:
                self.mousePositionX = positionX
                self.mousePositionY = positionY
                self.update_spectrum_plot()
        except Exception:
            pass

    def error_folder_name(self):  # GUI
        self.le_folderPath.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.le_folderPath.setStyleSheet("background-color: rgb(255,255,255)"))

    def error_laser_wavelength(self):  # GUI
        self.le_laser.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.le_laser.setStyleSheet("background-color: rgb(255,255,255)"))

    def error_background(self):  # GUI
        self.pb_background.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.pb_background.setStyleSheet("background-color: rgb(244,244,244)"))

    # Create
    def create_threads(self, *args):  # Keep? TODO
        self.sweepWorker = Worker(self.sweep, *args)
        self.sweepWorker.moveToThread(self.sweepThread)
        self.sweepThread.started.connect(self.sweepWorker.run)

        self.saveWorker = Worker(self.save_data_without_background, *args)
        self.saveWorker.moveToThread(self.saveThread)
        self.saveThread.started.connect(self.saveWorker.run)

    def create_matrix_raw_data(self):  # Model
        self.matrixRawData = np.zeros((self.height, self.width, self.dataLen))

    def create_matrix_rgb(self):  # Controller? GUI? TODO
        self.matrixRGB = np.zeros((self.height, self.width, 3))

    def create_plot_rgb(self):  # GUI
        self.graph_rgb.clear()
        self.plotViewBox = self.graph_rgb.addViewBox()
        self.plotViewBox.enableAutoRange()
        self.plotViewBox.invertY(True)
        self.plotViewBox.setAspectLocked()

    def create_plot_spectrum(self):  # GUI
        self.graph_spectre.clear()
        self.plotItem = self.graph_spectre.addPlot()
        self.plotSpectrum = self.plotItem.plot()
        self.plotRedRange = self.plotItem.plot()
        self.plotGreenRange = self.plotItem.plot()
        self.plotBlueRange = self.plotItem.plot()
        self.plotBlack = self.plotItem.plot()
        self.plotItem.enableAutoRange()

    def create_matrix_data_without_background(self):  # Model
        background = self.backgroundData
        background = background.reshape((1, 1, len(background)))
        background = np.vstack((background, ) * self.height)
        background = np.hstack((background, ) * self.width)
        self.matrixDataWithoutBackground = self.matrixRawData - background

    # Buttons
    def initialize_buttons(self):  # GUI
        self.pb_sweepSame.setIcons(QPixmap("./gui/misc/icons/sweep_same.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_hover.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_clicked.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_selected.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.pb_sweepAlternate.setIcons(QPixmap("./gui/misc/icons/sweep_alternate.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_hover.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_clicked.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_selected.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def enable_all_buttons(self):  # GUI
        self.cb_delete_background.setEnabled(True)
        self.cmb_selectDetection.setEnabled(True)
        self.cmb_selectLight.setEnabled(True)
        self.cmb_selectStage.setEnabled(True)
        self.cmb_magnitude.setEnabled(True)
        self.pb_save_without_background.setEnabled(True)
        self.pb_connectDetection.setEnabled(True)
        self.pb_sweepAlternate.setEnabled(True)
        self.pb_connectLight.setEnabled(True)
        self.pb_connectStage.setEnabled(True)
        self.pb_sweepSame.setEnabled(True)
        self.pb_background.setEnabled(True)
        self.sb_exposure.setEnabled(True)
        self.sb_acqTime.setEnabled(True)
        self.sb_height.setEnabled(True)
        self.sb_width.setEnabled(True)
        self.sb_step.setEnabled(True)
        self.tb_folderPath.setEnabled(True)
        self.le_fileName.setEnabled(True)

    def disable_all_buttons(self):  # GUI
        self.cb_delete_background.setEnabled(False)
        self.cmb_selectDetection.setEnabled(False)
        self.cmb_selectLight.setEnabled(False)
        self.cmb_selectStage.setEnabled(False)
        self.cmb_magnitude.setEnabled(False)
        self.pb_save_without_background.setEnabled(False)
        self.pb_connectDetection.setEnabled(False)
        self.pb_sweepAlternate.setEnabled(False)
        self.pb_connectLight.setEnabled(False)
        self.pb_connectStage.setEnabled(False)
        self.pb_sweepSame.setEnabled(False)
        self.pb_background.setEnabled(False)
        self.sb_exposure.setEnabled(False)
        self.sb_acqTime.setEnabled(False)
        self.sb_height.setEnabled(False)
        self.sb_width.setEnabled(False)
        self.sb_step.setEnabled(False)
        self.tb_folderPath.setEnabled(False)
        self.le_fileName.setEnabled(False)

    # Set
    def set_red_range(self):  # GUI
        self.sb_lowRed.setValue(self.mapping_on_spinBox(self.dSlider_red.get_left_thumb_value()))
        self.sb_highRed.setValue(self.mapping_on_spinBox(self.dSlider_red.get_right_thumb_value()))

        self.update_color()

    def set_green_range(self):  # GUI
        self.sb_lowGreen.setValue(self.mapping_on_spinBox(self.dSlider_green.get_left_thumb_value()))
        self.sb_highGreen.setValue(self.mapping_on_spinBox(self.dSlider_green.get_right_thumb_value()))

        self.update_color()

    def set_blue_range(self):  # GUI
        self.sb_lowBlue.setValue(self.mapping_on_spinBox(self.dSlider_blue.get_left_thumb_value()))
        self.sb_highBlue.setValue(self.mapping_on_spinBox(self.dSlider_blue.get_right_thumb_value()))

        self.update_color()

    def set_measure_unit(self):  # GUI
        if self.cmb_magnitude.currentText() == 'mm':
            self.order = 10**3

        elif self.cmb_magnitude.currentText() == 'um':
            self.order = 1

        elif self.cmb_magnitude.currentText() == 'nm':
            self.order = 10**(-3)

        else:
            print('What the hell is going on?!')

    def set_exposure_time(self, time_in_ms=None, update=True):  # Model
        if time_in_ms is not None:
            expositionTime = time_in_ms

        else:
            expositionTime = self.exposureTime

        self.spec.integration_time_micros(expositionTime * 1000)
        if update:
            self.set_integration_time()

    def set_integration_time(self):  # Model
        try:
            if self.integrationTimeAcq >= self.exposureTime:
                self.integrationCountAcq = self.integrationTimeAcq // self.exposureTime
                self.integrationTimeAcqRemainder_ms = self.integrationTimeAcq - (
                        self.integrationCountAcq * self.exposureTime)

            else:
                self.integrationCountAcq = 1

        except ValueError:
            print('nope, wrong value of integration:D')

        if self.integrationTimeAcqRemainder_ms > 3:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq + 1)
            self.changeLastExposition = 1

        else:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq)
            self.changeLastExposition = 0

    def set_range_to_wave(self):  # GUI
        self.minWaveLength = round(self.waves[0])
        self.maxWaveLength = round(self.waves[-1])

        self.rangeLen = self.maxWaveLength - self.minWaveLength

        self.sb_highRed.setMaximum(self.maxWaveLength)
        self.sb_lowRed.setMaximum(self.maxWaveLength-1)
        self.sb_highGreen.setMaximum(self.maxWaveLength)
        self.sb_lowGreen.setMaximum(self.maxWaveLength-1)
        self.sb_highBlue.setMaximum(self.maxWaveLength)
        self.sb_lowBlue.setMaximum(self.maxWaveLength-1)

        self.sb_highRed.setMinimum(self.minWaveLength)
        self.sb_lowRed.setMinimum(self.minWaveLength)
        self.sb_highGreen.setMinimum(self.minWaveLength)
        self.sb_lowGreen.setMinimum(self.minWaveLength)
        self.sb_highBlue.setMinimum(self.minWaveLength)
        self.sb_lowBlue.setMinimum(self.minWaveLength)
        self.sb_lowRed.setValue(self.minWaveLength)
        self.sb_highRed.setValue(round(self.rangeLen/3) + self.minWaveLength)
        self.sb_lowGreen.setValue(round(self.rangeLen/3) + self.minWaveLength + 1)
        self.sb_highGreen.setValue(round((self.rangeLen*(2/3)) + self.minWaveLength))
        self.sb_lowBlue.setValue(round((self.rangeLen*(2/3)) + self.minWaveLength+1))
        self.sb_highBlue.setValue(self.maxWaveLength)

    # Acquisition
    def spectrum_pixel_acquisition(self):  # Model
        # self.set_exposure_time()
        self.isAcquisitionDone = False

        while not self.isAcquisitionDone:
            self.liveAcquisitionData = self.read_data_live().tolist()
            self.integrate_data()
            self.dataPixel = np.mean(np.array(self.movingIntegrationData()), 0)

    def acquire_background(self):  # Model
        if self.folderPath == "":
            self.error_folder_name()

        else:
            try:
                self.disable_all_buttons()
                self.set_exposure_time()
                self.isAcquiringBackground = True
                self.spectrum_pixel_acquisition()
                self.backgroundData = self.dataPixel
                self.start_save(data=self.backgroundData)
                self.enable_all_buttons()

            except Exception as e:
                print(f"Error in acquire_background: {e}")

        self.isAcquiringBackground = False

    def integrate_data(self):  # Model
        self.isAcquisitionDone = False
        if self.expositionCounter < self.integrationCountAcq - 2:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1

        elif self.expositionCounter == self.integrationCountAcq - 2:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1
            if self.changeLastExposition:
                self.set_exposure_time(self.integrationTimeAcqRemainder_ms, update=False)

        else:
            self.set_exposure_time(update=False)
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.isAcquisitionDone = True
            self.expositionCounter = 0

    def read_data_live(self):
        return self.spec.intensities()[2:]

    def stop_acq(self):  # Model
        if self.isSweepThreadAlive:
            self.sweepThread.quit()
            self.isSweepThreadAlive = False
            self.countHeight = 0
            self.countWidth = 0
            self.countSpectrum = 0
            self.cmb_wave.setEnabled(True)

        else:
            print('Sampling already stopped.')

        self.enable_all_buttons()

    # Update
    def update_color(self):  # Controller
        try:
            self.matrixRGB_replace()
            self.update_rgb_plot()
            self.update_spectrum_plot()
        except Exception:
            pass

    def update_rgb_plot(self):  # GUI
        vb = pg.ImageItem(image=self.matrixRGB)
        self.plotViewBox.addItem(vb)

    def update_spectrum_plot(self):  # GUI
        if self.visualWithoutBackground:
            matrix = self.matrixDataWithoutBackground
        else:
            matrix = self.matrixRawData
        try:
            maximum = max(matrix[self.mousePositionY, self.mousePositionX, :])
            minimum = min(matrix[self.mousePositionY, self.mousePositionX, :]) - 1
        except Exception:
            maximum = 1
            minimum = 0

        if self.colorRangeViewEnable:
            lowRed = int(((self.sb_lowRed.value() - self.minWaveLength) / self.rangeLen) * self.dataLen)
            highRed = int(((self.sb_highRed.value() - self.minWaveLength) / self.rangeLen) * self.dataLen-1)
            lowGreen = int(((self.sb_lowGreen.value() - self.minWaveLength) / self.rangeLen) * self.dataLen)
            highGreen = int(((self.sb_highGreen.value() - self.minWaveLength) / self.rangeLen) * self.dataLen-1)
            lowBlue = int(((self.sb_lowBlue.value() - self.minWaveLength) / self.rangeLen) * self.dataLen)
            highBlue = int(((self.sb_highBlue.value() - self.minWaveLength) / self.rangeLen) * self.dataLen - 1)

            self.redRange = np.full(self.dataLen, minimum)
            self.redRange[lowRed] = maximum
            self.redRange[highRed] = maximum

            self.greenRange = np.full(self.dataLen, minimum)
            self.greenRange[lowGreen] = maximum
            self.greenRange[highGreen] = maximum

            self.blueRange = np.full(self.dataLen, minimum)
            self.blueRange[lowBlue] = maximum
            self.blueRange[highBlue] = maximum

            self.plotRedRange.setData(self.waves, self.redRange, pen=(255, 0, 0))
            self.plotGreenRange.setData(self.waves, self.greenRange, pen=(0, 255, 0))
            self.plotBlueRange.setData(self.waves, self.blueRange, pen=(0, 0, 255))
            self.plotBlack.setData(self.waves, np.full(self.dataLen, minimum), pen=(0, 0, 0))

        if not self.colorRangeViewEnable:
            self.plotRedRange.setData(self.waves, np.full(self.dataLen, minimum), pen=(0, 0, 0))
            self.plotGreenRange.setData(self.waves, np.full(self.dataLen, minimum), pen=(0, 0, 0))
            self.plotBlueRange.setData(self.waves, np.full(self.dataLen, minimum), pen=(0, 0, 0))
            self.plotBlack.setData(self.waves, np.full(self.dataLen, minimum), pen=(0, 0, 0))

        self.plotSpectrum.setData(self.waves, matrix[self.mousePositionY, self.mousePositionX, :])

    def update_range_to_wave(self):  # GUI
        self.minWaveLength = round(self.waves[0])
        self.maxWaveLength = round(self.waves[-1])

        self.rangeLen = self.maxWaveLength - self.minWaveLength

        self.sb_highRed.setMaximum(self.maxWaveLength)
        self.sb_lowRed.setMaximum(self.maxWaveLength - 1)
        self.sb_highGreen.setMaximum(self.maxWaveLength)
        self.sb_lowGreen.setMaximum(self.maxWaveLength - 1)
        self.sb_highBlue.setMaximum(self.maxWaveLength)
        self.sb_lowBlue.setMaximum(self.maxWaveLength - 1)

        self.sb_highRed.setMinimum(self.minWaveLength)
        self.sb_lowRed.setMinimum(self.minWaveLength)
        self.sb_highGreen.setMinimum(self.minWaveLength)
        self.sb_lowGreen.setMinimum(self.minWaveLength)
        self.sb_highBlue.setMinimum(self.minWaveLength)
        self.sb_lowBlue.setMinimum(self.minWaveLength)
        self.sb_lowRed.setValue(self.minWaveLength)
        self.sb_highRed.setValue(round(self.rangeLen / 3) + self.minWaveLength)
        self.sb_lowGreen.setValue(round(self.rangeLen / 3) + self.minWaveLength + 1)
        self.sb_highGreen.setValue(round((self.rangeLen * (2 / 3)) + self.minWaveLength))
        self.sb_lowBlue.setValue(round((self.rangeLen * (2 / 3)) + self.minWaveLength + 1))
        self.sb_highBlue.setValue(self.maxWaveLength)

    def matrix_raw_data_replace(self):  # Model
        self.matrixRawData[self.countHeight, self.countWidth, :] = np.array(self.dataPixel)
        self.dataPixel = []
        self.start_save(self.matrixRawData[self.countHeight, self.countWidth, :], self.countHeight, self.countWidth)

    def matrixRGB_replace(self):  # Controller? GUI? TODO
        if self.visualWithoutBackground:
            matrix = self.matrixDataWithoutBackground
        else:
            matrix = self.matrixRawData

        lowRed = int(((self.sb_lowRed.value() - self.minWaveLength) / self.rangeLen) * self.dataLen)
        highRed = int(((self.sb_highRed.value() - self.minWaveLength) / self.rangeLen) * self.dataLen)
        lowGreen = int(((self.sb_lowGreen.value() - self.minWaveLength) / self.rangeLen) * self.dataLen)
        highGreen = int(((self.sb_highGreen.value() - self.minWaveLength) / self.rangeLen) * self.dataLen)
        lowBlue = int(((self.sb_lowBlue.value() - self.minWaveLength) / self.rangeLen) * self.dataLen)
        highBlue = int(((self.sb_highBlue.value() - self.minWaveLength) / self.rangeLen) * self.dataLen)

        self.matrixRGB[:, :, 0] = matrix[:, :, lowRed:highRed].sum(axis=2)
        self.matrixRGB[:, :, 1] = matrix[:, :, lowGreen:highGreen].sum(axis=2)
        self.matrixRGB[:, :, 2] = matrix[:, :, lowBlue:highBlue].sum(axis=2)

        if self.cmb_set_maximum.currentIndex() == 0:
            self.matrixRGB = (self.matrixRGB / np.max(self.matrixRGB)) * 255

        elif self.cmb_set_maximum.currentIndex() == 1:
            maxima = self.matrixRGB.max(axis=2)
            maxima = np.dstack((maxima,) * 3)
            np.seterr(divide='ignore', invalid='ignore')
            self.matrixRGB /= maxima
            self.matrixRGB[np.isnan(self.matrixRGB)] = 0
            self.matrixRGB *= 255

        self.matrixRGB = self.matrixRGB.round(0)

    def mapping_on_slider(self, value):  # GUI
        return round(((value - self.minWaveLength)/self.rangeLen) * 255)

    def mapping_on_spinBox(self, value):  # GUI
        return round((value/255) * self.rangeLen+self.minWaveLength)

    def update_slider_status(self):  # GUI
        self.dSlider_red.set_left_thumb_value(self.mapping_on_slider(self.sb_lowRed.value()))
        self.dSlider_red.set_right_thumb_value(self.mapping_on_slider(self.sb_highRed.value()))
        self.dSlider_green.set_left_thumb_value(self.mapping_on_slider(self.sb_lowGreen.value()))
        self.dSlider_green.set_right_thumb_value(self.mapping_on_slider(self.sb_highGreen.value()))
        self.dSlider_blue.set_left_thumb_value(self.mapping_on_slider(self.sb_lowBlue.value()))
        self.dSlider_blue.set_right_thumb_value(self.mapping_on_slider(self.sb_highBlue.value()))

        if self.doSliderPositionAreInitialize:
            try:
                self.update_spectrum_plot()
            except Exception:
                pass
        else:
            self.doSliderPositionAreInitialize = True

    def colorRangeView_status(self):  # GUI
        if self.cb_colorRangeView.checkState() == 2:
            self.colorRangeViewEnable = True
        if self.cb_colorRangeView.checkState() == 0:
            self.colorRangeViewEnable = False
        try:
            self.update_spectrum_plot()
        except Exception:
            pass

    # Begin loop
    def begin(self):  # Model
        if not self.isSweepThreadAlive:
            if self.folderPath == "":
                self.error_folder_name()
            elif self.le_laser.text() == "":
                self.error_laser_wavelength()
            else:
                if self.stageDevice is None or self.spec is None:
                    self.connect_detection()
                    self.connect_stage()

                self.isSweepThreadAlive = True
                self.pb_saveData.setEnabled(True)
                self.pb_saveImage.setEnabled(True)
                self.cmb_wave.setEnabled(False)
                self.disable_all_buttons()
                self.create_plot_rgb()
                self.create_plot_spectrum()
                self.set_exposure_time()
                self.create_matrix_raw_data()
                self.create_matrix_rgb()
                self.sweepThread.start()

        else:
            print('Sampling already started.')

    def sweep(self, *args, **kwargs):  # TODO Controller?
        while self.isSweepThreadAlive:
            if self.countSpectrum <= (self.width*self.height):
                self.spectrum_pixel_acquisition()
                self.matrix_raw_data_replace()
                self.matrixRGB_replace()
                self.update_rgb_plot()

                if self.direction == "same":
                    try:
                        if self.countWidth < (self.width-1):
                            # wait for signal... (with a connect?)
                            self.countWidth += 1
                            self.move_stage()
                        elif self.countHeight < (self.height-1) and self.countWidth == (self.width-1):
                            # wait for signal...
                            self.countWidth = 0
                            self.countHeight += 1
                            self.move_stage()
                        else:
                            self.stop_acq()

                    except Exception as e:
                        print(f'error in sweep same: {e}')
                        self.stop_acq()

                elif self.direction == "other":
                    try:
                        if self.countHeight % 2 == 0:
                            if self.countWidth < (self.width-1):
                                # wait for signal...
                                self.countWidth += 1
                                self.move_stage()
                            elif self.countWidth == (self.width-1) and self.countHeight < (self.height-1):
                                # wait for signal...
                                self.countHeight += 1
                                self.move_stage()
                            else:
                                self.stop_acq()
                        elif self.countHeight % 2 == 1:
                            if self.countWidth > 0:
                                # wait for signal...
                                self.countWidth -= 1
                                self.move_stage()
                            elif self.countWidth == 0 and self.countHeight < (self.height-1):
                                # wait for signal...
                                self.countHeight += 1
                                self.move_stage()
                            else:
                                self.stop_acq()
                    except Exception as e:
                        print(f'error in sweep other: {e}')
                        self.stop_acq()

                self.countSpectrum += 1

            else:
                self.stop_acq()

    def move_stage(self):  # Model
        self.stageDevice.moveTo((self.positionSutter[0]+self.countWidth*self.step*self.order,
                                 self.positionSutter[1]+self.countHeight*self.step*self.order,
                                 self.positionSutter[2]))

    # Save
    def start_save(self, data=None, countHeight=None, countWidth=None):  # Model
        self.heightId = countHeight
        self.widthId = countWidth
        self.data = data
        self.save_capture_csv()

    def select_save_folder(self):  # GUI? Controller? Model? TODO
        self.folderPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if self.folderPath != "":
            self.le_folderPath.setText(self.folderPath)

    def save_capture_csv(self):  # Model
        if self.data is None:
            pass
        else:
            spectrum = self.data
            self.fileName = self.le_fileName.text()
            if self.fileName == "":
                self.fileName = "spectrum"

            fixedData = copy.deepcopy(spectrum)
            newPath = self.folderPath + "/" + "RawData"
            os.makedirs(newPath, exist_ok=True)
            if self.heightId is None and self.widthId is None:
                path = os.path.join(newPath, f"{self.fileName}_background")
            else:
                path = os.path.join(newPath, f"{self.fileName}_x{self.widthId}_y{self.heightId}")
            with open(path + ".csv", "w+") as f:
                for i, x in enumerate(self.waves):
                    f.write(f"{x},{fixedData[i]}\n")
                f.close()

        if self.countSpectrum == self.width*self.height-1 and self.isSweepThreadAlive:
            spectra = self.matrixRawData
            self.fileName = self.le_fileName.text()
            if self.fileName == "":
                self.fileName = "acquisitions"

            fixedData = copy.deepcopy(spectra)
            path = os.path.join(newPath, f"{self.fileName}_matrixRawData")
            with open(path + ".csv", "w+") as f:
                f.write("[")
                for i, x in enumerate(fixedData):
                    if i == 0:
                        f.write("[")
                    else:
                        f.write("\n\n[")
                    for ii, y in enumerate(x):
                        if ii == 0:
                            f.write("[")
                        else:
                            f.write("\n[")
                        for iii, z, in enumerate(y):
                            if iii != len(y)-1:
                                f.write(f"{z}, ")
                            else:
                                f.write(f"{z}")
                        f.write("]")
                    f.write("]")
                f.write("]")

                f.close()

    def save_image(self):  # Controller? GUI? TODO
        path = self.folderPath + "/"
        img = self.matrixRGB.astype(np.uint8)
        if self.fileName == "":
            plt.imsave(path + "matrixRGB.png", img)
        else:
            plt.imsave(path + self.fileName + "_matrixRGB.png", img)

    def save_matrixRGB(self):  # Controller? GUI? TODO
        path = self.folderPath + "/"
        fixedData = copy.deepcopy(self.matrixRGB)
        if self.fileName == "":
            file = "matrixRGB.csv"
        else:
            file = self.fileName + "_matrixRGB.csv"

        with open(path + file, "w+") as f:
            f.write("[")
            for i, x in enumerate(fixedData):
                if i == 0:
                    f.write("[")
                else:
                    f.write("\n\n[")
                for ii, y in enumerate(x):
                    if ii == 0:
                        f.write("[")
                    else:
                        f.write("\n[")
                    for iii, z, in enumerate(y):
                        if iii != len(y) - 1:
                            f.write(f"{z}, ")
                        else:
                            f.write(f"{z}")
                    f.write("]")
                f.write("]")
            f.write("]")

            f.close()

    def save_matrix_data_without_background(self):  # Model
        if not list(self.backgroundData):
            self.error_background()
        else:
            self.disable_all_buttons()
            self.create_matrix_data_without_background()
            self.saveThread.start()
            self.enable_all_buttons()

    def save_data_without_background(self, *args, **kwargs):  # Model
        matrix = self.matrixDataWithoutBackground
        newPath = self.folderPath + "/" + "UnrawData"
        os.makedirs(newPath, exist_ok=True)
        for i in range(self.height):
            for j in range(self.width):
                spectrum = matrix[i, j, :]
                self.fileName = self.le_fileName.text()
                if self.fileName == "":
                    self.fileName = "spectrum"
                path = os.path.join(newPath, f"{self.fileName}_withoutBackground_x{i}_y{j}")
                with open(path + ".csv", "w+") as f:
                    for ind, x in enumerate(self.waves):
                        f.write(f"{x},{spectrum[ind]}\n")
                    f.close()

        path = newPath + "/"
        if self.fileName == "":
            file = "matrixDataWithoutBackground.csv"
        else:
            file = self.fileName + "_matrixDataWithoutBackground.csv"

        with open(path + file, "w+") as f:
            f.write("[")
            for i, x in enumerate(matrix):
                if i == 0:
                    f.write("[")
                else:
                    f.write("\n\n[")
                for ii, y in enumerate(x):
                    if ii == 0:
                        f.write("[")
                    else:
                        f.write("\n[")
                    for iii, z, in enumerate(y):
                        if iii != len(y) - 1:
                            f.write(f"{z}, ")
                        else:
                            f.write(f"{z}")
                    f.write("]")
                f.write("]")
            f.write("]")

            f.close()

        # self.enable_all_buttons()
