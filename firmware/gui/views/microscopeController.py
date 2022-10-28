import hardwarelibrary.communication.serialport as sepo
import hardwarelibrary.motion.sutterdevice as sutter
from tools.CircularList import RingBuffer

from gui.modules import mockSpectrometer as Mock
import seabreeze.spectrometers as sb
from microscopeModel import Model

import matplotlib.pyplot as plt
import numpy as np
import copy
import os

class MicroscopeControl:
    def __init__(self):
        self.acq = Model()
        # self.waves = Mock.MockSpectrometer().wavelengths()[2:]
        # self.spec = Mock.MockSpectrometer()
        self.expositionCounter = 0
        # self.exposureTime = 1000
        # self.integrationTimeAcq = 5000
        self.integrationCountAcq = 0
        self.movingIntegrationData = None
        # self.isAcquiringBackground = False
        # self.dataPixel = []
        self.liveAcquisitionData = []
        self.integrationTimeAcqRemainder_ms = 0
        # self.isAcquisitionDone = False
        self.changeLastExposition = 0
        self.dataSep = 0
        self.dataLen = 0
        # self.backgroundData = []
        # self.matrixRawData = None
        self.positionSutter = None
        self.countSpectrum = 0
        self.countHeight = 0
        self.countWidth = 0
        self.heightId = None
        self.widthId = None
        self.saveData = None

    # SETTINGS
    def set_exposure_time(self, time_in_ms=None, update=True):
        if time_in_ms is not None:
            expositionTime = time_in_ms

        else:
            expositionTime = self.acq.exposureTime

        self.acq.spec.integration_time_micros(expositionTime * 1000)
        if update:
            self.set_integration_time()

    def set_integration_time(self):
        try:
            if self.acq.integrationTime >= self.acq.exposureTime:
                self.integrationCountAcq = self.acq.integrationTime // self.acq.exposureTime
                self.integrationTimeAcqRemainder_ms = self.acq.integrationTime - (
                        self.integrationCountAcq * self.acq.exposureTime)

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

    # ACQUISITION
    def spectrum_pixel_acquisition(self):
        # self.set_exposure_time()
        self.acq.isAcquisitionDone = False

        self.acq.waves = self.acq.spec.wavelengths()[2:]
        self.dataLen = len(self.acq.waves)
        self.dataSep = (max(self.acq.waves) - min(self.acq.waves)) / len(self.acq.waves)

        while not self.acq.isAcquisitionDone:
            self.liveAcquisitionData = self.read_data_live().tolist()
            self.integrate_data()
            self.acq.dataPixel = np.mean(np.array(self.movingIntegrationData()), 0)

    def acquire_background(self):  # bypass spectrum pixel acq??? TODO
        if self.acq.folderPath == "":
            # call self.error_folder_name()
            pass

        else:
            try:
                # call self.disable_all_buttons()
                self.set_exposure_time()
                self.spectrum_pixel_acquisition()
                self.acq.backgroundData = self.acq.dataPixel
                self.start_save(data=self.acq.backgroundData)
                # call self.enable_all_buttons()

            except Exception as e:
                print(f"Error in acquire_background: {e}")

    def integrate_data(self):
        self.acq.isAcquisitionDone = False
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
            self.acq.isAcquisitionDone = True
            self.expositionCounter = 0

    def read_data_live(self):
        return self.acq.spec.intensities()[2:]

    def connect_detection(self):
        if self.acq.laserWavelength == "":
            # call self.error_laser_wavelength()
            pass
        else:
            try:
                if self.acq.spectroLink == "MockSpectrometer":
                    self.acq.spec = Mock.MockSpectrometer()
                else:
                    self.acq.spec = sb.Spectrometer(self.acq.spectroLink)
                self.dataLen = len(self.acq.waves)
                self.dataSep = (max(self.acq.waves) - min(self.acq.waves)) / self.dataLen
                # call self.cmb_wave.setEnabled(True)
                self.set_exposure_time()
                # call self.set_range_to_wave()
                # call self.update_slider_status()
                # call self.cmb_wave.setEnabled(True)
            except:
                # call self.error_laser_wavelength()
                pass

    def connect_stage(self):
        if self.acq.stageIndex == 0:
            self.acq.stage = sutter.SutterDevice(serialNumber="debug")
            self.acq.stage.doInitializeDevice()
        else:
            # TODO will update with list provided by sepo.SerialPort.matchPorts(idVendor=4930, idProduct=1)...
            self.acq.stage = sutter.SutterDevice()
            self.acq.stage.doInitializeDevice()
        if self.acq.stage is None:
            raise Exception('The sutter is not connected!')
        self.positionSutter = self.acq.stage.position()

    def stop_acq(self):
        pass
        # TODO update function
        # if self.isSweepThreadAlive:
        #     self.sweepThread.quit()
        #     self.isSweepThreadAlive = False
        #     self.countHeight = 0
        #     self.countWidth = 0
        #     self.countSpectrum = 0
        #     self.cmb_wave.setEnabled(True)
        #
        # else:
        #     print('Sampling already stopped.')

        # self.enable_all_buttons()

    # Begin loop
    def begin(self):
        if not self.isSweepThreadAlive:  # TODO change the variable and in controller or model init?
            if self.acq.folderPath == "":
                # call self.error_folder_name()
                pass
            elif self.acq.laserWavelength == "":
                # call self.error_laser_wavelength()
                pass
            else:
                if self.acq.stage is None or self.acq.spec is None:
                    self.connect_detection()
                    self.connect_stage()

                self.isSweepThreadAlive = True  # TODO change variable... see earlier TODOS
                # self.pb_saveData.setEnabled(True)
                # self.pb_saveImage.setEnabled(True)
                # self.cmb_wave.setEnabled(False)
                # self.disable_all_buttons()
                # self.create_plot_rgb()
                # self.create_plot_spectrum()
                self.set_exposure_time()
                # self.create_matrix_raw_data()
                # self.create_matrix_rgb()
                self.countSpectrum = 0
                self.countHeight = 0
                self.countWidth = 0
                self.sweep()

        else:
            print('Sampling already started.')

    def sweep(self):
        while self.isSweepThreadAlive:  # TODO change variable name
            if self.countSpectrum <= (self.acq.width * self.acq.height):
                self.spectrum_pixel_acquisition()
                # self.matrix_raw_data_replace()
                # self.matrixRGB_replace()
                # self.update_rgb_plot()

                if self.acq.direction == "same":
                    try:
                        if self.countWidth < (self.acq.width - 1):
                            # wait for signal...
                            self.countWidth += 1
                            self.move_stage()
                        elif self.countHeight < (self.acq.height - 1) and self.countWidth == (self.acq.width - 1):
                            # wait for signal...
                            self.countWidth = 0
                            self.countHeight += 1
                            self.move_stage()
                        else:
                            self.stop_acq()

                    except Exception as e:
                        print(f'error in sweep same: {e}')
                        self.stop_acq()

                elif self.acq.direction == "other":
                    try:
                        if self.countHeight % 2 == 0:
                            if self.countWidth < (self.acq.width - 1):
                                # wait for signal...
                                self.countWidth += 1
                                self.move_stage()
                            elif self.countWidth == (self.acq.width - 1) and self.countHeight < (self.acq.height - 1):
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
                            elif self.countWidth == 0 and self.countHeight < (self.acq.height - 1):
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

    def move_stage(self):
        self.acq.stage.moveTo((self.positionSutter[0] + self.countWidth * self.acq.step * self.acq.stepMeasureUnit,
                               self.positionSutter[1] + self.countHeight * self.acq.step * self.acq.stepMeasureUnit,
                               self.positionSutter[2]))

    # Save
    def start_save(self, data=None, countHeight=None, countWidth=None):
        self.heightId = countHeight
        self.widthId = countWidth
        self.saveData = data
        self.save_capture_csv()

    def save_capture_csv(self):  # TODO generalize the save function(s)
        if self.saveData is None:
            pass
        else:
            spectrum = self.saveData
            if not self.acq.fileName:
                self.acq.fileName = "spectrum"

            fixedData = copy.deepcopy(spectrum)
            newPath = self.acq.folderPath + "/" + "RawData"
            os.makedirs(newPath, exist_ok=True)
            if self.heightId is None and self.widthId is None:
                path = os.path.join(newPath, f"{self.acq.fileName}_background")
            else:
                path = os.path.join(newPath, f"{self.acq.fileName}_x{self.widthId}_y{self.heightId}")
            with open(path + ".csv", "w+") as f:
                for i, x in enumerate(self.acq.waves):
                    f.write(f"{x},{fixedData[i]}\n")
                f.close()
