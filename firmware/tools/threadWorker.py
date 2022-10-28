from PyQt5.QtCore import *
import traceback
import logging


class WorkerSignals(QObject):
    status = pyqtSignal(str)
    finished = pyqtSignal()


class Worker(QObject):
    def __init__(self, workerFunction, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = workerFunction
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.kwargs["statusSignal"] = self.signals.status

    @pyqtSlot()
    def run(self):
        try:
            self.function(*self.args, **self.kwargs)
        except Exception as e:
            print("ERROR: ", e)
            traceback.print_exc()
        finally:
            self.signals.finished.emit()
