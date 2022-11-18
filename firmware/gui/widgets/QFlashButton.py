from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class QFlashButton(QPushButton):
    def __init__(self, *args, **kwargs):
        QPushButton.__init__(self, *args, **kwargs)
        self.flashColor = QColor(0, 255, 0)
        self.default_color = self.getColor()
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(1000)
        self.animation.setLoopCount(-1)
        self.animation.setStartValue(self.default_color)
        self.animation.setEndValue(self.default_color)
        self.animation.setKeyValueAt(0.1, self.flashColor)

    def start_flash(self):
        self.animation.start()

    def getColor(self):
        return self.palette().color(QPalette.Button)

    def setColor(self, value):
        if value == self.getColor():
            return
        palette = self.palette()
        palette.setColor(self.backgroundRole(), value)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def set_flash_color(self, r, g, b):
        self.flashColor = QColor(r, g, b)

    def reset_color(self):
        self.setColor(self.default_color)

    def stop_flash(self):
        self.animation.stop()
        self.reset_color()

    color = pyqtProperty(QColor, getColor, setColor)
