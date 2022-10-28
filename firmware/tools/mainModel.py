import logging
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QSettings
import os


log = logging.getLogger(__name__)


class MainModel(QObject):
    s_mouse_graph_position = pyqtSignal()
    s_show_delta = pyqtSignal()

    def __init__(self):
        super(MainModel, self).__init__()
        self._mouse_x = 0
        self._mouse_y = 0
        self._showDelta = False
        self._arrowDelta_x = 0
        self._arrowDelta_y = 0

    @property
    def exposureTime(self):
        return

    @exposureTime.setter
    def exposureTime(self, value):
        pass

    @property
    def mouseX(self):
        return self._mouse_x

    @property
    def mouseY(self):
        return self._mouse_y

    @property
    def mousePosition(self):
        return [self._mouse_x, self._mouse_y]

    @mousePosition.setter
    def mousePosition(self, value):
        self. _mouse_x = value[0]
        self._mouse_y = value[1]
        if not self._showDelta:
            self.s_mouse_graph_position.emit()
        elif self._showDelta:
            self.s_show_delta.emit()

    @property
    def arrowDeltaValueX(self):
        return self._arrowDelta_x

    @property
    def arrowDeltaValueY(self):
        return self._arrowDelta_y

    @property
    def arrowDelta(self):
        return [self._arrowDelta_x, self._arrowDelta_y]

    @arrowDelta.setter
    def arrowDelta(self, value):
        self._arrowDelta_x = value[0]
        self._arrowDelta_y = value[1]
        self._showDelta = True

    @property
    def showDelta(self):
        return self._showDelta

    @showDelta.setter
    def showDelta(self, value: bool):
        self._showDelta = value