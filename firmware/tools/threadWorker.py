from PyQt5.QtCore import *
import traceback
import logging


class WorkerSignals(QObject):
    status = pyqtSignal(str)
    finished = pyqtSignal()
    result = pyqtSignal(object)
    progress = pyqtSignal(str)


class Worker(QRunnable):
    def __init__(self, workerFunction, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = workerFunction
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        try:
            result = self.function(*self.args, **self.kwargs)
        except Exception as e:
            print("ERROR: ", e)
            traceback.print_exc()
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()
