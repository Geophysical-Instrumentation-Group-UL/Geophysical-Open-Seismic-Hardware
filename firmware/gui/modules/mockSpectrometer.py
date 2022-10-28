import numpy as np
import time


class MockSpectrometer:
    def __init__(self):
        self.exposureTime = 3000
        self.shutter = 0.2
        self.backgroundIntensity = 0.005
        self.noise = 0.01

        self._background = background_spectrum()
        self._source = halogen_spectrum()
        # todo: move bg and source to spectrum object
        # todo: calibration offset?

    def integration_time_micros(self, integration_time_micros: int):
        self.exposureTime = integration_time_micros

    def wavelengths(self) -> np.ndarray:
        return np.linspace(339.24, 1022.28, 2048)

    def intensities(self) -> np.ndarray:
        t = time.time()
        background = self._background * self.backgroundIntensity * self.exposureFactor
        source = self._source * self.exposureFactor * self.shutterFactor
        noise = np.random.uniform(0, self.noise, 2048)
        out = np.clip((background + source + noise) * 4095, 0, 4095)

        delta = time.time() - t
        sleepTime = self.exposureTime / 1000000 - delta
        if sleepTime > 0:
            time.sleep(sleepTime)
        return out

    @property
    def exposureFactor(self):
        return self.exposureTime / 3000

    @property
    def shutterFactor(self):
        return self.shutter ** 2 / 0.5


def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))


def halogen_spectrum():
    x = np.linspace(339.24, 1022.28, 2048)
    return gaussian(x, mu=600, sig=100) * 0.7 + gaussian(x, mu=700, sig=70) * 0.3


def background_spectrum():
    x = np.linspace(339.24, 1022.28, 2048)
    return gaussian(x, mu=550, sig=5) * 1 + gaussian(x, mu=610, sig=8) * 0.7 + \
           gaussian(x, mu=480, sig=15) * 0.2 + gaussian(x, mu=550, sig=200) * 0.1
