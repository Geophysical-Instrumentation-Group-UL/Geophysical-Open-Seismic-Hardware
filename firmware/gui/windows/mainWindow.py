from gui.dialog.helpDialog import HelpDialog
from gui.views.shotView import ShotView
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QTabWidget, QAction, QApplication
from PyQt5.QtCore import Qt, pyqtSlot, QFile, QTextStream
import logging
import os
from PyQt5 import uic

log = logging.getLogger(__name__)


MainWindowPath = os.path.dirname(os.path.realpath(__file__)) + '{}mainWindowUi.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainWindowPath)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, model=None):
        super(MainWindow, self).__init__()
        self.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.setupUi(self)
        self.model = model

        self.create_views_and_dialogs()
        self.setup_window_tabs()
        self.setup_statusBar()
        self.setup_menuBar()
        self.connect_buttons()
        self.connect_signals()

    def setup_window_tabs(self):
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)
        self.tabWidget.addTab(self.shotView, "ShotView")

    def setup_menuBar(self):
        self.helpAction = QAction(self)
        self.helpAction.setText("Help")
        self.menubar.addAction(self.helpAction)

    def setup_statusBar(self):
        self.statusbarMessage = QLabel()
        self.statusbar.addWidget(self.statusbarMessage)

    def create_views_and_dialogs(self):
        self.helpDialog = HelpDialog()
        self.shotView = ShotView(model=self.model)

    def connect_buttons(self):
        self.helpAction.triggered.connect(self.show_helpDialog)
        self.actionChange_Theme.triggered.connect(lambda: self.toggle_stylesheet(os.path.dirname(os.path.realpath(__file__)) + '\\..\\themes\\darkstyle\\darkstyle.qss'))

    def connect_signals(self):
        self.helpDialog.s_windowClose.connect(lambda: self.setEnabled(True))
        self.model.s_mouse_graph_position.connect(lambda: self.change_status_message("x:{:.2f}, y:{:.2f}".format(self.model.mouseX, self.model.mouseY)))
        self.model.s_show_delta.connect(lambda: self.change_status_message("x:{:.2f}, y:{:.2f}\t\t ∆x:{:.2f}, ∆y:{:.2f}".format(self.model.mouseX, self.model.mouseY, self.model.arrowDelta[0], self.model.arrowDelta[1])))

    def change_status_message(self, message):
        self.statusbarMessage.setText(message)

    def show_helpDialog(self):
        log.info('Help Dialog Opened')
        self.setEnabled(False)
        self.helpDialog.exec_()

    def toggle_stylesheet(self, filePath):
        '''
        Toggle the stylesheet to use the desired path in the Qt resource
        system (prefixed by `:/`) or generically (a path to a file on
        system).

        :path:      A full path to a resource or file on system
        '''

        # get the QApplication instance,  or crash if not set
        app = QApplication.instance()
        if app is None:
            raise RuntimeError("No Qt Application found.")

        styleFile = qss_file = open(filePath).read()
        app.setStyleSheet(styleFile)

