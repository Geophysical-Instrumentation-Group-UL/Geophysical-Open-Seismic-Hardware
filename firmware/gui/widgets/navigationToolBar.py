from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
import os

# imageFolder = os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + "\\fig"


class NavigationToolbar(NavigationToolbar2QT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        actions = self.findChildren(QAction)
        for a in actions:
            if a.text() not in ['Home', "Pan", "Zoom"]:
                self.removeAction(a)


    # def _icon(self, name):
    #     iconPath = os.path.join(imageFolder, name)
    #     if not os.path.exists(iconPath):
    #         return QIcon(os.path.join(imageFolder, 'home'))
    #
    #     return QIcon(iconPath)

# NavigationToolbar2QT._icon = NavigationToolbar._icon
