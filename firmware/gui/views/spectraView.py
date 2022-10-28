from PyQt5.QtWidgets import QWidget, QMessageBox, QCheckBox, QFileDialog
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread
import copy
import os
from pyqtgraph import LinearRegionItem, mkBrush, mkPen, SignalProxy, InfiniteLine, TextItem, ArrowItem
from PyQt5 import uic
import seabreeze.spectrometers as sb
from gui.modules import mockSpectrometer as mock
from tools.threadWorker import Worker
from tools.CircularList import RingBuffer
import numpy as np


import logging


log = logging.getLogger(__name__)

spectraViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "{0}spectraViewUi.ui".format(os.sep)
Ui_spectraView, QtBaseClass = uic.loadUiType(spectraViewUiPath)


class SpectraView(QWidget, Ui_spectraView):
    s_data_changed = pyqtSignal(dict)
    s_data_acquisition_done = pyqtSignal()

    # Initializing Functions

    def __init__(self, model=None):
        super(SpectraView, self).__init__()
        self.model = model
        self.setupUi(self)

        self.acqThread = QThread()
        self.isAcquisitionThreadAlive = False

        self.spec = None
        self.waves = None
        self.y = None
        self.dataLen = None
        self.deviceConnected = False

        self.plotItem = None
        self.xPlotRange = [350, 1000]
        self.yPlotRange = [0, 4120]
        self.cursorActivated = False
        self.clickCounter = 0
        self.dataPlotItem = None
        self.acqWorker = None
        self.cursorCurvePosition = []
        self.mode = "delta"
        self.deltaValues = []

        self.errorRejectedList = None
        self.maxAcceptedAbsErrorValue = 0.01
        self.rejectedXValues = []
        self.pyqtRegionList = []
        self.errorRegionsPoints = []
        self.errorRegionsIndexesLimits = []
        self.errorRegionsLimits = []
        self.errorBrush = mkBrush((255, 0, 0, 25))
        self.errorPen = mkPen((255, 0, 0, 180))
        self.dataSep = 0

        self.exposureTime = 50
        self.expositionCounter = 0
        self.changeLastExposition = 0

        self.integrationTimeAcq = 3000
        self.integrationTimeAcqRemainder_ms = 0
        self.integrationCountAcq = 0

        self.liveAcquisitionData = []
        self.temporaryIntegrationData = None
        self.movingIntegrationData = None
        self.displayData = None
        self.backgroundData = None
        self.filterData = None
        self.normalizationData = None
        self.normalizationMultiplierList = []

        self.isSpectrumNormalized = False
        self.isBackgroundRemoved = False
        self.isDataAnalysed = False

        self.launchIntegrationAcquisition = False

        self.isAcquiringFilter = False
        self.isAcquiringNormalization = False
        self.isAcquiringBackground = False
        self.isAcquiringIntegration = False
        self.isAcquisitionDone = False

        self.acquisitionType = ""

        self.backgroundWarningDisplay = True

        # Saving Data
        self.folderPath = ""
        self.fileName = ""
        self.autoindexing = False

        self.create_dialogs()
        self.connect_buttons()
        self.connect_signals()
        self.connect_checkbox()
        self.create_threads()
        self.create_plots()
        self.initialize_device()
        self.update_indicators()
        self.define_colors()

    def initialize_device(self):
        log.debug("Initializing devices...")
        try:
            devices = sb.list_devices()
            self.spec = sb.Spectrometer(devices[0])
            log.info("Devices:{}".format(devices))
            self.deviceConnected = True
        except IndexError as e:
            log.warning("No SpectrumDevice was found. Try connecting manually.")
            self.deviceConnected = False
            self.spec = mock.MockSpectrometer()
            log.info("No device found; Mocking Spectrometer Enabled.")

        self.set_exposure_time()

    def connect_buttons(self):
        self.pb_liveView.clicked.connect(self.toggle_live_view)

        self.pb_rmBackground.clicked.connect(self.save_background)
        self.pb_rmBackground.clicked.connect(self.update_indicators)

        self.pb_analyse.clicked.connect(lambda: setattr(self, "isAcquiringFilter", True))
        self.pb_analyse.clicked.connect(self.update_indicators)

        self.pb_normalize.clicked.connect(lambda: setattr(self, 'isAcquiringNormalization', True))
        self.pb_normalize.clicked.connect(lambda: self.update_indicators())

        self.sb_exposure.valueChanged.connect(lambda: setattr(self, 'exposureTime', self.sb_exposure.value()))
        self.sb_exposure.valueChanged.connect(self.set_exposure_time)

        self.sb_acqTime.valueChanged.connect(lambda: setattr(self, 'movingIntegrationData', None))
        self.sb_acqTime.valueChanged.connect(lambda: setattr(self, 'integrationTimeAcq', self.sb_acqTime.value()))
        self.sb_acqTime.valueChanged.connect(self.set_integration_time)

        self.pb_reset.clicked.connect(self.reset)

        self.sb_absError.valueChanged.connect(lambda: setattr(self, 'maxAcceptedAbsErrorValue', self.sb_absError.value()/100))
        self.sb_absError.valueChanged.connect(self.draw_error_regions)

        self.tb_folderPath.clicked.connect(self.select_save_folder)
        self.pb_saveData.clicked.connect(self.save_capture_csv)

        log.debug("Connecting GUI buttons...")

    def connect_checkbox(self):
        self.ind_rmBackground.clicked.connect(lambda:print("showBackground if available"))
        self.ind_normalize.clicked.connect(lambda: print("show normalisation if available"))
        self.ind_analyse.clicked.connect(lambda: print("show acquisition if available"))
        self.cb_cursor.toggled.connect(lambda: self.toggle_cursor(not self.cursorActivated))
        self.rb_free.toggled.connect(lambda: self.set_cursor_mode())
        self.rb_delta.toggled.connect(lambda: self.set_cursor_mode())

    def connect_signals(self):
        log.debug("Connecting GUI signals...")
        self.s_data_changed.connect(self.update_graph)
        self.s_data_changed.connect(self.update_indicators)
        # self.s_data_acquisition_done.connect(self.update_indicators)

    def create_threads(self, *args):
        self.acqWorker = Worker(self.manage_data_flow, *args)
        self.acqWorker.moveToThread(self.acqThread)
        self.acqThread.started.connect(self.acqWorker.run)

    def create_dialogs(self):
        self.warningDialog = QMessageBox()
        self.warningDialog.setIcon(QMessageBox.Information)
        self.warningDialog.setText("Your light source should be 'OFF' before removing the background signal.")
        self.warningDialog.setWindowTitle("Remove Background")
        self.warningDialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.doNotShow = QCheckBox("Do not show again.")
        self.warningDialog.setCheckBox(self.doNotShow)
        self.doNotShow.clicked.connect(lambda: setattr(self, 'backgroundWarningDisplay', 0))

    def create_plots(self):
        log.debug("Creating GUI plots...")
        self.pyqtgraphWidget.clear()
        self.plotItem = self.pyqtgraphWidget.addPlot()
        self.dataPlotItem = self.plotItem.plot()
        self.plotItem.enableAutoRange()

        # Create Cursor
        self.proxyClick = SignalProxy(self.plotItem.scene().sigMouseClicked, rateLimit=10, slot=self.mouseClicked)
        self.proxyMove = SignalProxy(self.plotItem.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.cursorlabel = TextItem(anchor=(50, 50))
        self.vLine = InfiniteLine(angle=90, movable=False)
        self.hLine = InfiniteLine(angle=0, movable=False)
        self.plotItem.addItem(self.vLine, ignoreBounds=True)
        self.plotItem.addItem(self.hLine, ignoreBounds=True)

        # Create graphical sprites
        self.arrows = []
        self.arrowText = []
        self.toggle_cursor(False)

    def define_colors(self):
        pass

    # General Cursor-Graph Interaction Functions

    def set_cursor_mode(self):
        if self.rb_delta.isChecked():
            self.mode = "delta"
        elif self.rb_free.isChecked():
            self.mode = "free"

    def toggle_cursor(self, state):
        self.cursorActivated = state

        if state:
            self.vLine.show()
            self.hLine.show()
            self.rb_delta.setEnabled(True)
            self.rb_free.setEnabled(True)
            self.set_cursor_mode()

        else:
            self.rb_delta.setEnabled(False)
            self.rb_free.setEnabled(False)
            self.hide_graph_sprites()
            self.remove_graph_arrows()

    def mouseMoved(self, evt):
        if self.cursorActivated:
            pos = evt[0]
            if self.plotItem.sceneBoundingRect().contains(pos):
                self.findClosestPoint(pos)
                self.vLine.setPos(self.cursorCurvePosition[0])
                self.hLine.setPos(self.cursorCurvePosition[1])
                self.model.mousePosition = self.cursorCurvePosition
        else:
            self.hide_graph_sprites()

    def hide_graph_sprites(self):
        self.vLine.hide()
        self.hLine.hide()

    def show_graph_sprites(self):
        self.vLine.show()
        self.hLine.show()
        for item1 in self.arrowText:
            item1.show()
        for item2 in self.arrows:
            item2.show()

    def remove_graph_arrows(self):
        self.clickCounter = 0
        for item1 in self.arrowText:
            self.plotItem.removeItem(item1)
        for item2 in self.arrows:
            self.plotItem.removeItem(item2)

    def findClosestPoint(self, pos):
        mousePoint = self.plotItem.vb.mapSceneToView(pos)
        if self.waves is None:
            self.cursorCurvePosition = [mousePoint.x(), mousePoint.y()]
        else:
            mx = np.array([abs(i - mousePoint.x()) for i in self.waves])
            self.index = mx.argmin()
            self.cursorCurvePosition = [self.waves[self.index], self.y[self.index]]

    def mouseClicked(self, evt):
        log.debug("Click event: {}, button {}".format(evt[0], evt[0].button))
        if self.cursorActivated and evt[0].double():
            log.debug("Double-click event: {}".format(evt[0]))
            if self.mode == "delta":
                self.manage_arrow_delta()
            elif self.mode == "free":
                self.manage_arrow_free()

        if evt[0].button() == 4:
            self.remove_graph_arrows()

    def manage_arrow_delta(self):
        if self.clickCounter < 2:
            self.clickCounter += 1
            self.arrows.append(ArrowItem(angle=-90))
            self.arrowText.append(
                TextItem("[{:.2f}, {:.2f}]".format(self.cursorCurvePosition[0], self.cursorCurvePosition[1])))
            self.plotItem.addItem(self.arrows[-1])
            self.plotItem.addItem(self.arrowText[-1])

            self.arrows[-1].setPos(self.cursorCurvePosition[0], self.cursorCurvePosition[1])
            self.arrowText[-1].setPos(self.cursorCurvePosition[0], self.cursorCurvePosition[1])
            self.deltaValues.append([self.cursorCurvePosition[0], self.cursorCurvePosition[1]])

        else:
            self.deltaValues = []
            self.model.showDelta = False
            self.remove_graph_arrows()
            self.clickCounter = 0

        if self.clickCounter == 2:
            deltaX = abs(self.deltaValues[0][0]-self.deltaValues[1][0])
            deltaY = abs(self.deltaValues[0][1] - self.deltaValues[1][1])
            self.model.arrowDelta = [deltaX, deltaY]

    def manage_arrow_free(self):
        if self.clickCounter < 10:
            self.clickCounter += 1
            self.arrows.append(ArrowItem(angle=-90))
            self.arrowText.append(
                TextItem("[{:.2f}, {:.2f}]".format(self.cursorCurvePosition[0], self.cursorCurvePosition[1])))
            self.plotItem.addItem(self.arrows[-1])
            self.plotItem.addItem(self.arrowText[-1])

            self.arrows[-1].setPos(self.cursorCurvePosition[0], self.cursorCurvePosition[1])
            self.arrowText[-1].setPos(self.cursorCurvePosition[0], self.cursorCurvePosition[1])
            self.deltaValues.append([self.cursorCurvePosition[0], self.cursorCurvePosition[1]])

        else:
            self.deltaValues = []
            self.model.showDelta = False
            self.remove_graph_arrows()
            self.clickCounter = 0

    # Low-Level Backend Graph Functions

    @pyqtSlot(dict)
    def update_graph(self, plotData):
        self.y = plotData["y"]
        self.dataPlotItem.setData(self.waves, self.y)

    def manage_data_flow(self, *args, **kwargs):
        self.waves = self.spec.wavelengths()[2:]
        self.dataLen = len(self.waves)
        self.dataSep = (max(self.waves) - min(self.waves)) / len(self.waves)

        while self.isAcquisitionThreadAlive:

            self.liveAcquisitionData = self.read_data_live().tolist()

            self.integrate_data()
            self.displayData = np.mean(np.array(self.movingIntegrationData()), 0)

            self.acquire_background()
            self.normalize_data()
            #self.hide_high_error_values()
            self.analyse_data()

            self.s_data_changed.emit({"y": self.displayData})

    def read_data_live(self, *args, **kwargs):
        return self.spec.intensities()[2:]

    def set_exposure_time(self, time_in_ms=None, update=True):
        if time_in_ms is not None:
            expositionTime = time_in_ms
        else:
            expositionTime = self.exposureTime
        self.spec.integration_time_micros(expositionTime * 1000)

        if update:
            self.set_integration_time()

    def set_integration_time(self, time_in_ms_view=None, time_in_ms_acq=None):
        try:
            if self.integrationTimeAcq >= self.exposureTime:
                self.integrationCountAcq = self.integrationTimeAcq // self.exposureTime
                self.integrationTimeAcqRemainder_ms = self.integrationTimeAcq - (self.integrationCountAcq * self.exposureTime)
                self.sb_acqTime.setStyleSheet('color: black')
            else:
                self.integrationCountAcq = 1
                self.sb_acqTime.setStyleSheet('color: red')

        except ValueError as e:
            log.error(e)
            self.sb_acqTime.setStyleSheet('color: red')

        if self.integrationTimeAcqRemainder_ms > 3:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq+1)
            self.changeLastExposition = 1
        else:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq)
            self.changeLastExposition = 0

    def integrate_data(self):
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

    def launch_integration_acquisition(self):
        if self.launchIntegrationAcquisition and not self.isAcquiringIntegration:
            self.expositionCounter = 0
            self.isAcquiringIntegration = True
            self.launchIntegrationAcquisition = False
            log.info("Integration Acquiring...")

        elif self.isAcquiringIntegration:
            if not self.isAcquisitionDone:
                percent = int(self.expositionCounter * 100 / self.integrationCountAcq)
                if percent in [25, 50, 75, 100]:
                    log.debug(
                    "Acquisition frame: {} over {} : {}%".format(self.expositionCounter, self.integrationCountAcq,
                                                                int(self.expositionCounter * 100 / self.integrationCountAcq)))
            elif self.isAcquisitionDone:
                self.temporaryIntegrationData = np.mean(np.array(self.movingIntegrationData()), 0)
                self.isAcquiringIntegration = False
                log.debug("Integration acquired.")

    def acquire_background(self):
        if self.isAcquiringBackground:
            self.launchIntegrationAcquisition = True
            self.launch_integration_acquisition()

            if self.isAcquisitionDone:
                self.backgroundData = self.temporaryIntegrationData
                self.isBackgroundRemoved = True
                self.isAcquiringBackground = False
                log.info("Background acquired.")

        if self.isBackgroundRemoved:
            self.displayData = self.displayData - self.backgroundData

    def normalize_data(self):
        if self.isAcquiringNormalization:
            self.launchIntegrationAcquisition = True
            self.launch_integration_acquisition()

            if self.isAcquisitionDone:
                self.normalizationMultiplierList = []
                self.normalizationData = self.displayData
                maximumCount = max(self.normalizationData)
                for i in self.normalizationData:
                    if i != 0:
                        self.normalizationMultiplierList.append(float(1/i))
                    else:
                        self.normalizationMultiplierList.append(0)

                self.isSpectrumNormalized = True
                self.isAcquiringNormalization = False
                log.info("Normalization Spectrum acquired.")
                self.plotItem.setRange(yRange=[0, 1.1])
                self.draw_error_regions()

        if self.isSpectrumNormalized:
            self.displayData = [a * b for a, b in zip(self.displayData, self.normalizationMultiplierList)]

    def hide_high_error_values(self):
        if self.isSpectrumNormalized:
            #log.debug(self.errorRegionIndexesLimits)
            for region in self.errorRegionIndexesLimits:
                for i in range(region[0], region[1]):
                    self.displayData[i] = self.displayData[i] * 0

    def draw_error_regions(self):
        self.verify_absolute_error()
        self.remove_old_error_regions()
        self.find_error_regions()
        self.add_error_regions()

    def verify_absolute_error(self):
        if self.isSpectrumNormalized:
            brute = np.array(self.movingIntegrationData()) * np.array(self.normalizationMultiplierList)
            sd = np.std(brute, axis=0)
            # log.debug("Standard Deviation of points:{}".format(sd))
            self.errorRejectedList = []
            counter = 0
            for i, error in enumerate(sd):
                if error >= self.maxAcceptedAbsErrorValue:
                    self.errorRejectedList.append(True)
                else:
                    self.errorRejectedList.append(False)
                    counter += 1
            self.rejectedXValues = self.waves[self.errorRejectedList]
            log.debug("Amount of accepted values:{}".format(counter))

    def find_error_regions(self):
        regionsLimits, regionPoints, regionIndexes, regionIndexesLimits = self.segregate_same_regions(
            self.rejectedXValues, 15 * self.dataSep)

        self.errorRegionsIndexesLimits = regionIndexesLimits
        self.errorRegionsLimits = regionsLimits
        log.debug("Rejected Regions:{}".format(self.errorRegionsLimits))

    def add_error_regions(self):
        try:
            self.pyqtRegionList = []
            for region in self.errorRegionsLimits:
                errorRegion = LinearRegionItem(brush=self.errorBrush, pen=self.errorPen, movable=False)
                errorRegion.setRegion(region)
                self.pyqtRegionList.append(errorRegion)
                self.plotItem.addItem(self.pyqtRegionList[-1])
        except Exception as e:
            log.error(e)

    def remove_old_error_regions(self):
        try:
            for region in self.pyqtRegionList:
                self.plotItem.removeItem(region)
        except Exception as e:
            log.error(e)

    def analyse_data(self):
        pass

    def reset(self):
        self.dataPlotItem.clear()
        self.remove_old_error_regions()
        self.plotItem.setRange(xRange=self.xPlotRange, yRange=self.yPlotRange)
        self.backgroundData = None
        self.isBackgroundRemoved = False
        self.normalizationData = None
        self.normalizationMultiplierList = None
        self.isSpectrumNormalized = False
        self.update_indicators()
        log.info("All parameters and acquisition reset.")

    # High-Level Front-End Functions

    def toggle_live_view(self):
        if not self.isAcquisitionThreadAlive:
            try:
                self.acqThread.start()
                self.isAcquisitionThreadAlive = True
                self.pb_liveView.start_flash()
                self.cb_cursor.setEnabled(True)

            except Exception as e:
                log.error(e)
                self.spec = mock.MockSpectrometer()

        else:
            self.acqThread.terminate()
            self.pb_liveView.stop_flash()
            self.isAcquisitionThreadAlive = False
            self.cb_cursor.setEnabled(False)
            if self.cb_cursor.isChecked():
                self.cb_cursor.toggle()

        self.update_indicators()

    def visualize_any_acquisition(self):
        pass

    def update_indicators(self):
        if self.isAcquisitionThreadAlive:
            self.ind_rmBackground.setEnabled(True)
            self.ind_normalize.setEnabled(True)
            self.ind_analyse.setEnabled(True)
            self.enable_all_buttons()
            if self.backgroundData is None:
                self.ind_rmBackground.setStyleSheet("QCheckBox::indicator{background-color: #db1a1a;}")
                try:
                    self.ind_rmBackground.clicked.disconnect()
                except Exception:
                    pass
            else:
                self.ind_rmBackground.setStyleSheet("QCheckBox::indicator{background-color: #55b350;}")

            if self.isAcquiringBackground:
                self.ind_rmBackground.setStyleSheet("QCheckBox::indicator{background-color: #f79c34;}")

            if self.isAcquiringNormalization:
                self.ind_normalize.setStyleSheet("QCheckBox::indicator{background-color: #f79c34;}")

            if not self.isSpectrumNormalized:
                self.ind_normalize.setStyleSheet("QCheckBox::indicator{background-color: #db1a1a;}")
                try:
                    self.ind_normalize.clicked.disconnect()
                except Exception:
                    pass
            else:
                self.ind_normalize.setStyleSheet("QCheckBox::indicator{background-color: #55b350;}")

            if self.filterData is None:
                self.ind_analyse.setStyleSheet("QCheckBox::indicator{background-color: #db1a1a;}")
                try:
                    self.ind_analyse.clicked.disconnect()
                except Exception:
                    pass
            else:
                self.ind_analyse.setStyleSheet("QCheckBox::indicator{background-color: #55b350;}")
        else:
            self.disable_all_buttons()
            self.ind_rmBackground.setEnabled(False)
            self.ind_normalize.setEnabled(False)
            self.ind_analyse.setEnabled(False)
            self.ind_rmBackground.setStyleSheet("QCheckBox::indicator{background-color: #9e9e9e;}")
            self.ind_normalize.setStyleSheet("QCheckBox::indicator{background-color: #9e9e9e;}")
            self.ind_analyse.setStyleSheet("QCheckBox::indicator{background-color: #9e9e9e;}")

    def disable_all_buttons(self):
        self.pb_rmBackground.setEnabled(False)
        self.pb_normalize.setEnabled(False)
        self.pb_analyse.setEnabled(False)

    def enable_all_buttons(self):
        self.pb_rmBackground.setEnabled(True)
        self.pb_normalize.setEnabled(True)
        self.pb_analyse.setEnabled(True)

    def save_background(self):
        if self.backgroundWarningDisplay:
            answer = self.warningDialog.exec_()
            if answer == QMessageBox.Ok:
                self.isAcquiringBackground = 1
            elif answer == QMessageBox.Cancel:
                log.debug("Background data not taken.")

        else:

            self.isAcquiringBackground = 1
            self.update_indicators()
            self.disable_all_buttons()

    @staticmethod
    def segregate_same_regions(inputList, sep):
        listOfRegions = [[]]
        listOfRegionsIndexes = [[]]
        newRegion = 0
        for i, v in enumerate(inputList):

            if i == 0:
                if inputList[1] <= inputList[0] + sep:
                    listOfRegions[-1].append(inputList[0])
                    listOfRegionsIndexes[-1].append(int(i))

            elif inputList[i] <= inputList[i - 1] + sep:
                if newRegion:
                    listOfRegions[-1].append(inputList[i - 1])
                    listOfRegionsIndexes[-1].append(int(i - 1))
                    newRegion = 0
                listOfRegions[-1].append(inputList[i])
                listOfRegionsIndexes[-1].append(int(i))

            else:
                listOfRegions.append([])
                listOfRegionsIndexes.append([])
                newRegion = 1

        listOfLimits = []
        listOfIndexesLimits = []
        if listOfRegions:
            for i, region in enumerate(listOfRegions):
                if region:
                    listOfLimits.append([min(region), max(region)])
                    listOfIndexesLimits.append([min(listOfRegionsIndexes[i]), max(listOfRegionsIndexes[i])])

        return listOfLimits, listOfRegions, listOfRegionsIndexes, listOfIndexesLimits

    # Data Capture Methods

    def select_save_folder(self):
        self.folderPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if self.folderPath != "":
            self.le_folderPath.setText(self.folderPath)

    def toggle_autoindexing(self):
        pass

    def save_capture_csv(self):
        self.fileName = self.le_fileName.text()
        if self.folderPath == "":
            pass

        elif self.fileName == "":
            pass

        else:
            fixedData = copy.deepcopy(self.displayData)
            path = os.path.join(self.folderPath, self.fileName)
            with open(path+".csv", "w+") as f:
                for i, x in enumerate(self.waves):
                    f.write(f"{x},{fixedData[i]}\n")
                f.close()



 #  TODO:
 #  remove background, normalize (take ref, create norm, norm stream)
