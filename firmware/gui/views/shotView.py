from PyQt5.QtWidgets import QWidget, QMessageBox, QCheckBox, QFileDialog, QSpacerItem, QSizePolicy
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread, QThreadPool
import copy
import os
from pyqtgraph import LinearRegionItem, mkBrush, mkPen, SignalProxy, InfiniteLine, TextItem, ArrowItem
from PyQt5 import uic
import seabreeze.spectrometers as sb
from gui.modules import mockSpectrometer as mock
from gui.widgets.navigationToolBar import NavigationToolbar
from tools.threadWorker import Worker
from tools.CircularList import RingBuffer
from tools.stack import Stack
import numpy as np
import serial
from serial.tools import list_ports
import time
import logging
import matplotlib.pyplot as plt



log = logging.getLogger(__name__)

shotViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "{0}shotViewUi.ui".format(os.sep)
Ui_shotView, QtBaseClass = uic.loadUiType(shotViewUiPath)


class ShotView(QWidget, Ui_shotView):
    s_data_changed = pyqtSignal(dict)
    s_is_trigged = pyqtSignal(bool)
    s_data_acquisition_done = pyqtSignal()

    # Initializing Functions

    def __init__(self, model=None):
        super(ShotView, self).__init__()
        self.model = model
        self.setupUi(self)

        self.acqThread = QThread()

        self.threadpool = QThreadPool()
 
        self.warningDialog = None


        self.deviceConnected = False
        self.comPortAvailable = []
        self.comPortName = None
        self.comPort = None
        self.DCvoltageUpholeList = ['40','60','80','100']
        self.DCvoltageUphole = None
        self.numberOfShuttleList = ['1','2','3']
        self.numberOfShuttle = None

        self.list_out = []
        self.axes = []
        self.currentStack = None

        self.acquisitionDuration = 50
        self.expositionCounter = 0

        self.acquisitionFrequency = 4

        self.stackName = None
        self.nextStackName = None
        self.shotCounter = 0
        self.isTrigged = False

      
        self.create_dialogs()
        self.connect_buttons()
        self.connect_checkbox()
        self.connect_lineEdit()
        self.initToolbar()

     

    def initialize_device(self):
        log.debug("Initializing devices...")
        try:
            devices = sb.list_devices()
            self.spec = sb.Spectrometer(devices[0])
            log.info("Devices:{}".format(devices))
            self.deviceConnected = True
        except IndexError as e:
            log.warning("No SpectrumDevice was found. Try connecting manually.")
            self.deviceConnected = False
            self.spec = mock.MockSpectrometer()
            log.info("No device found; Mocking Spectrometer Enabled.")

    def initGraph(self):
        self.mpl_graph.canvas.fig.clear()
        x = np.linspace(0, 1, 1000)
        y = np.linspace(0, 0.1, 1000)

        self.axes = [self.mpl_graph.canvas.fig.add_subplot(self.numberOfShuttle,1,i+1) for i in range(self.numberOfShuttle)]

        for i in range(self.numberOfShuttle):
            if i > 0:
                self.axes[i].get_shared_x_axes().join(self.axes[i], self.axes[i-1])
                self.axes[i].get_shared_y_axes().join(self.axes[i], self.axes[i-1])
            self.axes[i].plot(x, y)
            self.axes[i].set_title('Shuttle {}'.format(i+1))
            self.axes[i].set_ylabel('Accel (g)')
        
        self.axes[-1].set_xlabel('Time (s)')
        self.mpl_graph.canvas.fig.tight_layout()

        self.mpl_graph.canvas.draw()

    def initToolbar(self):
        self.realToolbar = NavigationToolbar(self.mpl_graph.canvas, self.mpl_graph)
        # spacer = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayoutNav.addWidget(self.realToolbar)
        # self.verticalLayoutNav.addItem(spacer)
        self.realToolbar.update()
        self.realToolbar.push_current()

    def connect_buttons(self):
        self.sb_duration.valueChanged.connect(self.set_acquisition_duration)

        self.sb_acqFreq.valueChanged.connect(self.set_acquisition_frequency)

        self.pb_newStack.clicked.connect(self.configure_create_new_stack)

        self.pb_arm.clicked.connect(self.arm)

        self.pb_collect.clicked.connect(self.collect)

        self.pb_showStack.clicked.connect(self.show_stack)

        self.pb_finishStack.clicked.connect(self.finish_stack)

        self.pb_acquireBackground.clicked.connect(self.acquire_background)
        

        self.show_comPort_available()


        self.disable_control_buttons()



        # self.sb_absError.valueChanged.connect(lambda: setattr(self, 'maxAcceptedAbsErrorValue', self.sb_absError.value()/100))
        # self.sb_absError.valueChanged.connect(self.draw_error_regions)

        # self.tb_folderPath.clicked.connect(self.select_save_folder)
        # self.pb_saveData.clicked.connect(self.save_capture_csv)

        log.debug("Connecting GUI buttons...")

    def connect_lineEdit(self):
        self.le_newStack.textChanged.connect(lambda: setattr(self, 'nextStackNAme', self.le_newStack.text()))
        self.tb_status.setPlainText("")

    def connect_checkbox(self):
        self.cb_comPort.currentIndexChanged.connect(self.set_comPort)
        self.cb_DCvoltageUphole.addItems(self.DCvoltageUpholeList)
        self.cb_DCvoltageUphole.currentIndexChanged.connect(self.set_DCvoltageUphole)
        self.cb_numberOfShuttle.addItems(self.numberOfShuttleList)
        self.cb_numberOfShuttle.currentIndexChanged.connect(self.set_numberOfShuttle)

    def create_dialogs(self):
        self.warningDialog = QMessageBox()
        self.warningDialog.setIcon(QMessageBox.Information)
        self.warningDialog.setText("System is armed, waiting for trigger")

    def show_comPort_available(self):
        comPortList = list_ports.comports()
        self.comPortAvailable = comPortList
        self.cb_comPort.clear()       # delete all items from comboBox
        for ports in self.comPortAvailable:
            self.cb_comPort.addItems([str(ports.name)]) # add the actual content of self.comboData
        self.cb_comPort.update()

    def set_comPort(self):
        self.comPortName = self.cb_comPort.currentText()
        self.comPort = serial.Serial(self.comPortName, 115200)
        self.tb_status.append("COM port set to: " + self.comPortName)

    def set_DCvoltageUphole(self):
        self.DCvoltageUphole = int(self.cb_DCvoltageUphole.currentText())
        self.tb_status.append("Source voltage set to: " + str(self.DCvoltageUphole) + " V")

    def set_numberOfShuttle(self):
        self.numberOfShuttle = int(self.cb_numberOfShuttle.currentText())
        self.tb_status.append("Number of shuttle set to: " + str(self.numberOfShuttle))

    def set_acquisition_frequency(self):
        self.acquisitionFrequency = self.sb_acqFreq.value()
        self.tb_status.append("Acquisition frequency set to: " + str(self.acquisitionFrequency) + ' Hz')
    
    def set_acquisition_duration(self):
        self.acquisitionDuration = self.sb_duration.value()
        self.tb_status.append("Acquisition duration set to: " + str(self.acquisitionDuration) + ' ms')

    def set_stack_name(self):
        self.stackName = self.le_newStack.text()

    def configure_create_new_stack(self):
        self.set_stack_name()
        self.set_comPort()
        self.set_numberOfShuttle()
        self.set_acquisition_duration()
        self.set_acquisition_frequency()
        self.currentStack = Stack(self.comPort, str(self.acquisitionFrequency), str(self.acquisitionDuration), self.stackName,self.numberOfShuttle)
        self.shotCounter = 0
        self.disable_configuration_buttons()
        self.enable_control_buttons()
        self.tb_status.clear()
        self.tb_status.append("New stack created : {}.".format(self.stackName))
        self.tb_status.append("Acquisition frequency: {} Hz.".format(self.acquisitionFrequency))
        self.tb_status.append("Acquisition duration: {} ms.".format(self.acquisitionDuration))
        self.tb_status.append("Number of shuttle: {}.".format(self.numberOfShuttle)) 
        self.tb_status.append("COM port set to : {}.".format(self.comPortName))  
        self.initGraph()

        for shuttle in range(self.numberOfShuttle):
            message = self.currentStack.configWorker(str(shuttle+1)) 
            [self.tb_status.append(i) for i in message]
        
    def thread_complete(self):
        print("THREAD COMPLETE!")
    
    def arm(self):
        self.isTrigged = False
        command = 'arm'
        self.comPort.write("{}".format(command).encode())
        line = self.comPort.read_until("...".encode()) # waits for the ok of the leader (very fast, does not block he GUI long enough to be annoying)

        self.tb_status.append(line.decode("utf-8")) 
        self.tb_status.append("Armed, waiting for trigger.")
        self.pb_arm.start_flash()
        self.pb_collect.setEnabled(False)
        self.pb_acquireBackground.setEnabled(False)
        self.pb_showStack.setEnabled(False)
        self.pb_finishStack.setEnabled(False)
        

        workerr = Worker(self.waitForTrig)
        workerr.signals.result.connect(self.print_message)
        workerr.signals.finished.connect(self.thread_complete)
        self.threadpool.start(workerr)
              
    def collect(self):
        worker = Worker(self.collect_data)
        worker.signals.result.connect(self.print_message)
        worker.signals.finished.connect(self.thread_complete)
        self.threadpool.start(worker)
        
    def finish_stack(self):
        self.enable_configuration_buttons()
        self.disable_control_buttons()
        self.tb_status.append("Stack  " + self.stackName + " is finished, please configure a new one.")
        self._shotCounter = 0
        self.comPort.close()

    def waitForTrig(self,progress_callback):
        line = self.serialRead("ed".encode())
        line = line.decode("utf-8")
        self.pb_arm.stop_flash()
        self.pb_collect.setEnabled(True)
        self.pb_arm.setEnabled(False)
        progress_callback.emit(line)
        self.tb_status.append(line)
        self.shotCounter += 1
        self.tb_status.append("shot count : {}".format(self.shotCounter))

    def collect_data(self,progress_callback):
        self.list_out = []
        for i in range(self.numberOfShuttle):
            out = self.currentStack.harvest('{}'.format(i+1),show=False)
            self.tb_status.append("shuttle {} harvested".format(i+1))
            self.list_out.append(out)
        
        self.currentStack.save2file(self.list_out, self.shotCounter)
        self.tb_status.append("Data saved to file.")
        time.sleep(2) # to let the time to write the file
        self.update_graph()
        self.pb_acquireBackground.setEnabled(True)
        self.pb_showStack.setEnabled(True)
        self.pb_finishStack.setEnabled(True)
        self.pb_arm.setEnabled(True)

    def show_stack(self):
        self.list_out = self.currentStack.loadStack()
        for sensors in self.list_out:
            sensors = sensors / self.shotCounter
        self.update_graph()

    def acquire_background(self):
        workerd = Worker(self.acquire_background_worker)
        workerd.signals.result.connect(self.print_message)
        workerd.signals.finished.connect(self.thread_complete)
        self.threadpool.start(workerd)

    def acquire_background_worker(self,progress_callback):
        self.autoTrigger()
        time.sleep(1)
        self.collect_data(progress_callback)

    def autoTrigger(self):
        self.comPort.write("background".encode())

    def serialSend(self, data):
        self.comPort.write(data)

    def serialRead(self,until):
        line = self.comPort.read_until(until)
        return line

    def print_message(self, message):
        self.tb_status.append(message)

    def update_graph(self):
        for i in range(self.numberOfShuttle):
            self.axes[i].cla()
            time_data = self.list_out[i][0,:]
            x_data = self.list_out[i][1,:]
            y_data = self.list_out[i][2,:]
            z_data = self.list_out[i][3,:]
            self.axes[i].plot(time_data,x_data, label="X")
            self.axes[i].plot(time_data,y_data, label="Y")
            self.axes[i].plot(time_data,z_data, label="Z")
            self.axes[i].legend()
            self.axes[i].set_xlabel('time [s]')
            self.axes[i].set_ylabel("Amplitude [V]")
        self.mpl_graph.canvas.draw()

    def disable_configuration_buttons(self):
        self.cb_comPort.setEnabled(False)
        self.cb_numberOfShuttle.setEnabled(False)
        self.sb_acqFreq.setEnabled(False)
        self.sb_duration.setEnabled(False)
        self.le_newStack.setEnabled(False)
        self.pb_newStack.setEnabled(False)
    
    def disable_control_buttons(self):
        self.pb_finishStack.setEnabled(False)
        self.pb_collect.setEnabled(False)
        self.pb_arm.setEnabled(False)
        self.pb_acquireBackground.setEnabled(False)
        self.pb_showStack.setEnabled(False)


    def enable_configuration_buttons(self):
        self.cb_comPort.setEnabled(True)
        self.cb_numberOfShuttle.setEnabled(True)
        self.sb_acqFreq.setEnabled(True)
        self.sb_duration.setEnabled(True)
        self.le_newStack.setEnabled(True)
        self.pb_newStack.setEnabled(True)
    
    def enable_control_buttons(self):
        self.pb_finishStack.setEnabled(True)
        self.pb_collect.setEnabled(True)
        self.pb_arm.setEnabled(True)
        self.pb_acquireBackground.setEnabled(True)
        self.pb_showStack.setEnabled(True)
