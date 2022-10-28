from PyQt5.QtWidgets import QAbstractButton, QSizePolicy
from PyQt5.Qt import QPainter, QSize


class QIconButton(QAbstractButton):
    def __init__(self, pixmap=None, pixmapHover=None, pixmapPressed=None, pixmapSelected=None, parent=None):
        super(QIconButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmapHover = pixmapHover
        self.pixmapPressed = pixmapPressed
        if pixmapSelected is not None:
            self.pixmapSelected = pixmap

        self.pressed.connect(self.update)
        self.released.connect(self.update)
        self.released.connect(self.toggle)
        self.setInitialSizePolicy()
        self.status = False

    def paintEvent(self, event):
        if None in [self.pixmap, self.pixmapHover, self.pixmapPressed, self.pixmapSelected]:
            return

        else:
            if self.underMouse():
                pix = self.pixmapHover
            elif self.isDown():
                pix = self.pixmapPressed
            elif self.status:
                pix = self.pixmapSelected
            else:
                pix = self.pixmap

            painter = QPainter(self)
            painter.drawPixmap(event.rect(), pix)

    def enterEvent(self, event):
        self.update()

    def leaveEvent(self, event):
        self.update()

    def sizeHint(self):
        return QSize(50, 50)

    def setIcons(self, pixmap, pixmapHover, pixmapPressed, pixmapSelected=None):
        self.pixmap = pixmap
        self.pixmapHover = pixmapHover
        self.pixmapPressed = pixmapPressed
        if pixmapSelected is not None:
            self.pixmapSelected = pixmap

    def setInitialSizePolicy(self):
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

    def toggle(self):
        self.status = not self.status