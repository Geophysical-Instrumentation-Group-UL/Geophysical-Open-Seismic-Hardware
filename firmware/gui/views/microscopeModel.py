from typing import NamedTuple
import seabreeze.spectrometers as sb
import hardwarelibrary


class DataTuple(NamedTuple):
    x: int = None
    y: int = None
    spectrum: list = None


class BackgroundTuple(NamedTuple):
    title: str = 'background'
    spectrum: list = None


class Model:
    stageDevices = []  # find list from hardware...
    stageDevices.insert(0, "Debug")
    stageDevices.append("real Sutter")
    stageIndex = 0
    stageLink = stageDevices[stageIndex]
    stage = None

    specDevices = sb.list_devices()
    specDevices.insert(0, "MockSpectrometer")
    specIndex = 0
    spectroLink = specDevices[specIndex]
    spec = None

    folderPath: str = None
    fileName: str = None
    laserWavelength: int = None
    width: int = 2
    height: int = 2
    step: int = 1
    stepMeasureUnit: float = 10**3
    exposureTime: int = 500
    integrationTime = 3000
    isAcquiring: bool = False
    isAcquisitionDone: bool = False  # change by notification?? TODO
    backgroundData: tuple = None
    waves: list = None
    dataPixel: list = None
    direction = "same"  # or "other"

    def createDataPixelTuple(self, x: int, y: int, spectrum: list):
        return DataTuple(x, y, spectrum)

    def createBackgroundTuple(self, spectrum):
        BackgroundTuple(spectrum=spectrum)

    def listSpecDevices(self):
        devices = []
        for i, spec in enumerate(self.specDevices):
            devices.append(str(spec))
        return devices
