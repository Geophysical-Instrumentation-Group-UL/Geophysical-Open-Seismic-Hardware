from PyQt5.QtCore import QThread, QMutex
import threading


class QStoppableThread(QThread):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stop_event = threading.Event()
        self.mutex = threading.Lock()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()
