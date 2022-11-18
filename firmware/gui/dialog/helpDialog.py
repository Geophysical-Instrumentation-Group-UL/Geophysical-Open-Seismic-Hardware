from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, pyqtSignal
import logging
import os
from PyQt5 import uic

log = logging.getLogger(__name__)

helpDialogUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}helpDialogUi.ui'.format(os.sep)
Ui_helpDialog, QtBaseClass = uic.loadUiType(helpDialogUiPath)


class HelpDialog(QDialog, Ui_helpDialog):

    s_windowClose = pyqtSignal()

    def __init__(self):
        super(HelpDialog, self).__init__()
        self.setupUi(self)
        self.setAttribute(Qt.WA_AlwaysStackOnTop)

    def closeEvent(self, event):
        self.s_windowClose.emit()

