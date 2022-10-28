__author__ = "Marc-André Vigneault"
__copyright__ = "Copyright 2021-2022, Marc-André Vigneault"
__credits__ = ["Marc-André Vigneault"]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Marc-André Vigneault"
__email__ = "marc-andre.vigneault@ulaval.ca"
__status__ = "Development"


from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from gui.windows.mainWindow import MainWindow
from tools.mainModel import MainModel
import sys
import ctypes
import logging
import logging.config
from logging.handlers import RotatingFileHandler
import os

log = logging.getLogger(__name__)


if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))


class App(QApplication):
    def __init__(self, sys_argv):
        super(App, self).__init__(sys_argv)

        sys.excepthook = self.handle_exception
        self.init_logging()
        log.debug("This is the MAIN THREAD")

        self.setAttribute(Qt.AA_EnableHighDpiScaling)
        self.setStyle("Fusion")

        self.mainModel = MainModel()
        self.mainWindow = MainWindow(model=self.mainModel)
        self.mainWindow.setWindowTitle("opt-id")
        self.mainWindow.show()

    @staticmethod
    def init_logging():
        logger = logging.getLogger()
        logger.setLevel(logging.NOTSET)

        # Console Handler
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s\t (%(name)-25.25s) (thread:%(thread)d) (line:%(lineno)5d)\t[%(levelname)-5.5s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Log Error File Handler
        os.makedirs(application_path + "{0}log".format(os.sep), exist_ok=True)
        handler = RotatingFileHandler(application_path + "{0}log{0}opt-id.log".format(os.sep), maxBytes=2.3 * 1024 * 1024, backupCount=5)
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s\t (%(name)-30.30s) (thread:%(thread)d) (line:%(lineno)5d)\t[%(levelname)-5.5s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        log.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


def main():
    # Makes the icon in the taskbar as well.
    appID = "opt-id"  # arbitrary string
    if os.name == 'nt':
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appID)
    elif os.name == 'posix':
        pass
    app = App(sys.argv)
    app.setWindowIcon(QIcon(application_path + "{0}gui{0}misc{0}logo{0}logo3.ico".format(os.sep)))
    app.mainWindow.setWindowIcon(QIcon(application_path + "{0}gui{0}misc{0}logo{0}logo3.ico".format(os.sep)))
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

