print('loading libs...')
import os
import datetime
from getmac import get_mac_address
print('loaded os and datatime...')
import time
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc

print('loaded PyQt...')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

# from smu.keithley2450 import keithley_2450
from devices.keithley2450 import keithley_2450
from devices.smu_simulation import SMUSimulation

print('loaded matplotlib.pyplot...')
import pyvisa

print('loaded pyvisa...')

class MainWindow(qtw.QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # your code will go here
        self.filepath = None
        # change class to SMU object, all self.Keithley change to self.SMU with function
        # self.Keithley = None
        #self.SMU = keithley_2450()
        self.SMU = SMUSimulation()
        self.save_data = False
        self.software_version = {'free': 0,
                                 'limited': 1,
                                 'unlimited': 2}
        # self.sw_version = self.software_version['free']
        self.sw_version = self.software_version['unlimited']
        # self.sw_version = self.software_version['unlimited']
        self.MAC_list = ['34:73:5a:d3:37:32', # Dell personal Labtop
                         'e4:54:e8:58:4f:9e' # office computer
                         ]
        self.meas_mode = 'IV'
        self.state = {'initialize': 0,
                      'wait_for_event': 1,
                      'start': 2,
                      'stop': 3,
                      'exit': 4,
                      'save_data': 5}
        # change the beginning event to Initialize!
        self.currState = self.state['initialize']
        self.nextState = None
        self.started = False

        # time variables
        self.start_time = time.time()
        self.current_time = time.time()

        # plot data
        self.logy_curr_data = []
        self.logy_all_data = []
        # collected of all data
        self.x_alldata = []
        self.y_alldata = []
        self.repeat = 0
        # current measurement data
        self.x_vals = []
        self.y_vals = []
        # self.index = count()
        self.index = int(0)

        # rt data collection
        # change to the display data

        # file for recording
        self.f = None

        # graph display mode
        self.yscale = 'linear'

        # Hardcode data for the Keithley connection
        self.visaResourceName = 'GPIB1::1::INSTR'
        self.nplc = 1
        # activeTerminal = Front/Rear (enum)
        self.startV = float(-1)
        self.stopV = float(1)
        self.stepV = float(0.1)
        self.numberStep = round((self.stopV - self.startV) / self.stepV)

        # list of voltage that will be applied to the device
        self.listV = []
        self.currentV = None
        self.currentI = None
        # create instance for connecting to the device
        self.rm = pyvisa.ResourceManager()
        # print(self.rm.list_resources())

        '''User Interface'''
        self.setWindowTitle('Source Measurement Units realtimeIV')
        self.resize(2400, 1800)

        # create figure
        self.figure = plt.figure(figsize=(120, 60))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # start_button
        self.start_button = qtw.QPushButton('start', self)
        self.start_button.clicked.connect(self.start_clicked)

        # stop_button
        self.stop_button = qtw.QPushButton('stop', self)
        self.stop_button.clicked.connect(self.stop_clicked)

        # exit button
        self.exit_button = qtw.QPushButton('exit', self)
        self.exit_button.clicked.connect(self.exit_clicked)

        # Keithley connect
        self.visa_label = qtw.QLabel('Visa name')
        self.visa_name = qtw.QComboBox()
        self.instruments_list = self.rm.list_resources()
        for i in range(len(self.instruments_list)):
            item = self.instruments_list.__getitem__(i)
            if 'GPIB' in item:
                self.visa_name.addItem(item, i)

        self.terminal_label = qtw.QLabel('terminal')
        self.terminal_value = qtw.QComboBox()
        self.terminal_value.addItem('front', 'FRON')
        self.terminal_value.addItem('rear', 'REAR')

        # parameter for IV measurement
        self.source_delay_time_label = qtw.QLabel('Sour. Delay Time (ms)')
        self.source_delay_time_value = qtw.QLineEdit()
        self.source_delay_time_value.setText('50')
        self.voltage_range_label = qtw.QLabel('V range')
        self.voltage_range_combo = qtw.QComboBox()
        self.voltage_range_combo.addItem('Auto', 0)
        self.voltage_range_combo.addItem('20mV', 0.02)
        self.voltage_range_combo.addItem('200mV', 0.2)
        self.voltage_range_combo.addItem('2V', 2)
        self.voltage_range_combo.addItem('20V', 20)
        self.voltage_range_combo.addItem('200V', 200)
        self.voltage_range_combo.setCurrentText('2V')

        self.from_voltage_label = qtw.QLabel('from V')
        self.from_voltage_value = qtw.QLineEdit()
        self.from_voltage_value.setText('-1')
        self.to_voltage_label = qtw.QLabel('to V')
        self.to_voltage_value = qtw.QLineEdit()
        self.to_voltage_value.setText('1')
        self.step_voltage_label = qtw.QLabel('step V')
        self.step_voltage_value = qtw.QLineEdit()
        self.step_voltage_value.setText('0.1')

        self.current_range_label = qtw.QLabel('I range')
        self.current_range_combo = qtw.QComboBox()
        self.current_range_combo.addItem('10nA', 10e-9)
        self.current_range_combo.addItem('100nA', 100e-9)
        self.current_range_combo.addItem('1uA', 1e-6)
        self.current_range_combo.addItem('10uA', 10e-6)
        self.current_range_combo.addItem('100uA', 100e-6)
        self.current_range_combo.addItem('1mA', 1e-3)
        self.current_range_combo.addItem('10mA', 10e-3)
        self.current_range_combo.addItem('100mA', 100e-3)
        self.current_range_combo.addItem('1A', 1)
        self.current_range_combo.setCurrentText('100uA')
        # NPLC settings
        self.nplc_label = qtw.QLabel('nplc')
        self.nplc_value = qtw.QComboBox()
        self.nplc_value.addItem('Fast', 0.01)
        self.nplc_value.addItem('Medium', 0.10)
        self.nplc_value.addItem('Normal', 1.00)
        self.nplc_value.addItem('High Accuracy', 10.00)
        self.nplc_value.setCurrentText('Normal')

        # measurement mode
        self.measure_mode_label = qtw.QLabel('Mea. Mode')
        self.measure_mode_combo = qtw.QComboBox()
        self.measure_mode_combo.addItem('IV', 0)
        self.measure_mode_combo.addItem('RT', 1)
        self.measure_mode_combo.setCurrentText('IV')
        self.measure_mode_combo.activated.connect(self.measure_mode_change)

        # parameter for RT measurements
        self.rt_voltage_range_label = qtw.QLabel('V Range')
        self.rt_voltage_range_combo = qtw.QComboBox()
        self.rt_voltage_range_combo.addItem('Auto', 0)
        self.rt_voltage_range_combo.addItem('20mV', 0.02)
        self.rt_voltage_range_combo.addItem('200mV', 0.2)
        self.rt_voltage_range_combo.addItem('2V', 2)
        self.rt_voltage_range_combo.addItem('20V', 20)
        self.rt_voltage_range_combo.addItem('200V', 200)
        self.rt_voltage_range_combo.setCurrentText('2V')

        self.rt_voltage_set_label = qtw.QLabel('V set')
        self.rt_voltage_set_value = qtw.QLineEdit()
        self.rt_voltage_set_value.setText('0.5')

        self.rt_current_range_label = qtw.QLabel('I Range')
        self.rt_current_range_combo = qtw.QComboBox()
        self.rt_current_range_combo.addItem('10nA', 10e-9)
        self.rt_current_range_combo.addItem('100nA', 100e-9)
        self.rt_current_range_combo.addItem('1uA', 1e-6)
        self.rt_current_range_combo.addItem('10uA', 10e-6)
        self.rt_current_range_combo.addItem('100uA', 100e-6)
        self.rt_current_range_combo.addItem('1mA', 1e-3)
        self.rt_current_range_combo.addItem('10mA', 10e-3)
        self.rt_current_range_combo.addItem('100mA', 100e-3)
        self.rt_current_range_combo.addItem('1A', 1)
        self.rt_current_range_combo.setCurrentText('100uA')

        self.rt_aperture_label = qtw.QLabel('Aperture (s)')
        self.rt_aperture_value = qtw.QLineEdit()
        self.rt_aperture_value.setText('1')

        # create layout
        self.layout = qtw.QHBoxLayout()
        self.setLayout(self.layout)

        # create left_layout
        self.left_layout = qtw.QVBoxLayout()
        self.layout.addLayout(self.left_layout)

        # create Box for Keithley connection
        # self.label.setStyleSheet("font-weight: bold")
        self.Keithley_Box = qtw.QGroupBox('Keithley Connection',
                                          alignment=qtc.Qt.AlignHCenter,
                                          flat=True)
        self.Keithley_Box.setStyleSheet('QGroupBox:title {'
                                        'subcontrol-origin: margin;'
                                        'subcontrol-position: top center;'
                                        'padding-left: 10px;'
                                        'padding-right: 10px;}')
        # self.Keithley_Box.setStyleSheet('font-weight: bold')
        self.Keithley_layout = qtw.QGridLayout()
        self.Keithley_Box.setLayout(self.Keithley_layout)
        self.Keithley_layout.addWidget(self.visa_label, 1, 1)
        self.Keithley_layout.addWidget(self.visa_name, 1, 2, 1, 3)
        self.Keithley_layout.addWidget(self.terminal_label, 2, 1)
        self.Keithley_layout.addWidget(self.terminal_value, 2, 3)
        self.Keithley_layout.addWidget(self.nplc_label, 3, 1)
        self.Keithley_layout.addWidget(self.nplc_value, 3, 3)
        self.Keithley_layout.addWidget(self.measure_mode_label, 4, 1)
        self.Keithley_layout.addWidget(self.measure_mode_combo, 4, 3)

        self.left_layout.addWidget(self.Keithley_Box)

        # and a tab here and move the items belongs to IV to the Tab1
        self.tabs_IV_RT = qtw.QTabWidget()
        self.tab_IV = qtw.QWidget()
        self.tab_RT = qtw.QWidget()
        self.tabs_IV_RT.addTab(self.tab_IV, 'IV')
        self.tabs_IV_RT.addTab(self.tab_RT, 'RT')
        self.left_layout.addWidget(self.tabs_IV_RT)
        self.tab_IV_layout = qtw.QFormLayout()
        self.tab_IV.setLayout(self.tab_IV_layout)
        self.tab_IV_layout.addRow(self.source_delay_time_label, self.source_delay_time_value)
        self.tab_IV_layout.addRow(self.voltage_range_label, self.voltage_range_combo)
        self.tab_IV_layout.addRow(self.from_voltage_label, self.from_voltage_value)
        self.tab_IV_layout.addRow(self.to_voltage_label, self.to_voltage_value)
        self.tab_IV_layout.addRow(self.step_voltage_label, self.step_voltage_value)
        self.tab_IV_layout.addRow(self.current_range_label, self.current_range_combo)

        self.tab_RT_layout = qtw.QFormLayout()
        self.tab_RT.setLayout(self.tab_RT_layout)
        self.tab_RT_layout.addRow(self.rt_voltage_range_label, self.rt_voltage_range_combo)
        self.tab_RT_layout.addRow(self.rt_voltage_set_label, self.rt_voltage_set_value)
        self.tab_RT_layout.addRow(self.rt_current_range_label, self.rt_current_range_combo)
        self.tab_RT_layout.addRow(self.rt_aperture_label, self.rt_aperture_value)

        # Folder location name, folder search button, file name
        self.fileDialog_box = qtw.QGroupBox('File and Plot Dialog', alignment=qtc.Qt.AlignHCenter, flat=True)
        self.fileDialog_box.setStyleSheet(('QGroupBox:title {'
                                           'subcontrol-origin: margin;'
                                           'subcontrol-position: top center;'
                                           'padding-left: 10px;'
                                           'padding-right: 10px;}'))
        self.fileDialog_layout = qtw.QGridLayout()
        self.fileDialog_box.setLayout(self.fileDialog_layout)

        self.sw_version_label = qtw.QLabel('Software version: ')

        folder_location_label = qtw.QLabel('File Location')
        self.folder_location_text = qtw.QLineEdit(os.getcwd())

        search_folder_button = qtw.QPushButton('Folder')
        search_folder_button.clicked.connect(self.folder_clicked)
        file_name_label = qtw.QLabel('File Name')
        self.file_name_text = qtw.QLineEdit('data')

        # log or linear display of the graph
        self.log_linear_combo = qtw.QComboBox()
        self.log_linear_combo.addItem('linear')
        self.log_linear_combo.addItem('log')
        graph_yscale = qtw.QLabel('y-scale')
        self.log_linear_combo.activated.connect(self.graph_scale)
        self.clear_graph_button = qtw.QPushButton('Clear Graph', self)
        self.clear_graph_button.clicked.connect(self.clear_graph_clicked)

        self.fileDialog_layout.addWidget(folder_location_label, 1, 1)
        self.fileDialog_layout.addWidget(self.folder_location_text, 2, 2, 1, 3)
        self.fileDialog_layout.addWidget(search_folder_button, 2, 1)
        self.fileDialog_layout.addWidget(file_name_label, 3, 1)
        self.fileDialog_layout.addWidget(self.file_name_text, 3, 3)
        self.fileDialog_layout.addWidget(graph_yscale, 4, 1)
        self.fileDialog_layout.addWidget(self.log_linear_combo, 4, 3)
        self.fileDialog_layout.addWidget(self.clear_graph_button, 5, 3)
        self.fileDialog_layout.addWidget(self.sw_version_label, 6, 1)

        self.left_layout.addWidget(self.fileDialog_box)
        # End File Dialog GUI

        # Communcation Dialog
        self.communication_box = qtw.QGroupBox('Communication')
        self.communication_layout = qtw.QVBoxLayout()
        self.communication_box.setLayout(self.communication_layout)

        self.communication_text = qtw.QTextEdit()
        self.communication_layout.addWidget(self.communication_text)

        self.left_layout.addWidget(self.communication_box)

        # save file location layout

        self.right_layout = qtw.QVBoxLayout()
        self.layout.addLayout(self.right_layout)

        self.right_layout.addWidget(self.toolbar)
        self.right_layout.addWidget(self.canvas)

        # button layout horizontal

        btn_layout = qtw.QHBoxLayout()
        btn_layout.addItem(qtw.QSpacerItem(0, 0, qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Minimum))
        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        btn_layout.addWidget(self.exit_button)

        self.right_layout.addLayout(btn_layout)
        '''end of user interface'''

        '''user setting saving'''
        self.setting_window = qtc.QSettings('KeithleyIV_RT', 'windows size')
        self.setting_variable = qtc.QSettings('KeithleyIV_RT', 'user interface')

        # time out, this function needs to go to the starter
        self.timer = qtc.QTimer()
        self.timer.timeout.connect(self.timeOutEvent)
        # time_out = round(self.nplc_value.currentData()*16.67) + round(float(self.source_delay_time_value.text()))+ 50
        # self.timer.start(time_out)  # timeout in  ms
        # self.timeOutEvent()

        # your code ends here
        self.show()

        self.switcher = {
            self.state['initialize']: self.initializer,
            self.state['start']: self.starter,
            self.state['stop']: self.stoper,
            self.state['exit']: self.exiter,
            self.state['wait_for_event']: self.waiter,
            self.state['save_data']: self.saver
        }

        # call state machine for the first state
        self.state_machine_function()

    # function for time out generator
    def timer_function(self, time_out):
        # self.timer = qtc.QTimer()
        # self.timer.timeout.connect(self.timeOutEvent)
        self.timer.start(time_out)
        # call the timeOutEvent function directly after iv/rt_starter
        self.timeOutEvent()


    '''event connected to functions'''

    def initializer(self):
        # should load parameters from previous measurement
        print('init program here')
        # self.message('initialization')
        '''load variables here'''
        self.message('initializer')

        try:
            self.resize(self.setting_window.value('window_size'))
            self.move(self.setting_window.value('window_position'))
            # user interface parameters
            self.visa_name.setCurrentText(self.setting_variable.value('visa_name'))
            self.terminal_value.setCurrentText(self.setting_variable.value('terminal'))
            self.nplc_value.setCurrentText(self.setting_variable.value('nplc'))
            self.measure_mode_combo.setCurrentText(self.setting_variable.value('mea_mode'))
            self.tabs_IV_RT.setCurrentIndex(self.measure_mode_combo.currentData())

            # # IV Parameters
            self.source_delay_time_value.setText(self.setting_variable.value('sour_delay_time'))
            self.voltage_range_combo.setCurrentText(self.setting_variable.value('v_range'))
            self.from_voltage_value.setText(self.setting_variable.value('from_v'))
            self.to_voltage_value.setText(self.setting_variable.value('to_v'))
            self.step_voltage_value.setText(self.setting_variable.value('step_v'))
            self.current_range_combo.setCurrentText(self.setting_variable.value('i_range'))

            # RT parameters
            self.rt_voltage_range_combo.setCurrentText(self.setting_variable.value('rt_v_range'))
            self.rt_voltage_set_value.setText(self.setting_variable.value('rt_v_set'))
            self.rt_current_range_combo.setCurrentText(self.setting_variable.value('rt_i_range'))
            self.rt_aperture_value.setText(self.setting_variable.value('aperture'))

            # # file and Plot Dialog
            self.folder_location_text.setText(self.setting_variable.value('save_folder'))
            self.file_name_text.setText(self.setting_variable.value('file_name'))
            self.log_linear_combo.setCurrentText(self.setting_variable.value('y_scale'))

            # set current parameter correspondingly
            self.yscale = self.log_linear_combo.currentText()
            self.meas_mode = self.measure_mode_combo.currentText()

        except:
            pass

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.exit_button.setEnabled(True)
        self.measure_mode_combo.setEnabled(True)
        self.currState = self.state['wait_for_event']

        # check version
        if self.sw_version == self.software_version['free']:
            self.save_data = False
            self.sw_version_label.setText('software version: Free')
            self.show_popup('free-version, saving data is not included')
        elif self.sw_version == self.software_version['limited']:
            # check if the MAC address is in the list of license
            local_MAC = get_mac_address(interface='Ethernet')
            # print(local_MAC)
            if local_MAC in self.MAC_list:
                self.save_data = True
                self.sw_version_label.setText('software version: limited')
            else:
                self.sw_version = self.software_version['free']
                self.sw_version_label.setText('software version: free')
                self.save_data = False
        elif self.sw_version == self.software_version['unlimited']:
            self.save_data = True
            self.sw_version_label.setText('software version: unlimited')
        else:
            pass

    def start_clicked(self):
        self.currState = self.state['start']
        self.state_machine_function()
        # self.currState = self.state_machine_function(currState,state)

    def stop_clicked(self):
        self.currState = self.state['stop']
        self.state_machine_function()
        # currState = state_machine_function(currState,state)

    def folder_clicked(self):
        # call the QFileDialog to return the current selected folder
        # self.folder_location_text
        currentLocation = qtw.QFileDialog.getExistingDirectory(
            self,
            caption='select a folder',
            directory=os.getcwd()
        )
        self.folder_location_text.setText(currentLocation)

    def graph_scale(self):
        self.yscale = self.log_linear_combo.currentText()
        # print(self.yscale)
        self.message(self.yscale)

    def clear_graph_clicked(self):

        self.clear_data()

        self.figure.clear()
        self.canvas.draw()
        # clear history of figure

    def measure_mode_change(self):
        self.meas_mode = self.measure_mode_combo.currentText()
        # change the mode, the repeat value set back to 0

        self.clear_data()

        # print(self.meas_mode)
        self.message(self.meas_mode)
        self.tabs_IV_RT.setCurrentIndex(self.measure_mode_combo.currentData())

    def clear_data(self):
        self.repeat = 0
        self.index = 0
        # clear data
        self.x_vals.clear()
        self.y_vals.clear()
        self.x_alldata.clear()
        self.y_alldata.clear()

        self.logy_curr_data.clear()
        self.logy_all_data.clear()

    def timeOutEvent(self):
        # print('time out events')
        # check if started == True -> record

        if self.meas_mode == 'IV':
            self.iv_get_plot()
        elif self.meas_mode == 'RT':
            self.rt_get_plot()
        else:
            pass

    # get and plot data in IV mode
    def iv_get_plot(self):
        self.message('iv get and plot')
        # print('went into iv_get_plot')

        if self.started == True and self.index <= self.numberStep:
            self.currentV = self.listV[self.index]
            # read out the current with the corresponding voltage
            self.currentI = self.read_current_out(self.currentV)
            self.x_vals.append(self.currentV)
            self.y_vals.append(self.currentI)
            self.logy_curr_data.append(abs(self.currentI))
            # plot logarithmic scale
            self.index += 1
            self.figure.clear()
            ax = self.figure.add_subplot(1, 1, 1)
            plt.yscale(self.yscale)
            plt.autoscale(enable=True, axis='y')

            # plt.grid(color='green', linestyle='--', linewidth=0.5)
            ax.grid(which='major', color='grey', linewidth=1)
            ax.grid(which='minor', color='darkgrey', linestyle=':', linewidth=0.8)
            ax.minorticks_on()
            plt.title("IV measurement", fontsize=20)
            plt.xlabel("voltage (V)", fontsize=18)
            plt.ylabel("current (A)", fontsize=18)
            plt.rcParams['xtick.labelsize'] = 16
            plt.rcParams['ytick.labelsize'] = 16
            # plot history data
            for i in range(self.repeat):
                if self.yscale == 'linear':
                    ax.plot(self.x_alldata[i], self.y_alldata[i])
                else:
                    # plot log data if in log scale
                    ax.plot(self.x_alldata[i], self.logy_all_data[i])
            # plot current data
            if self.yscale == 'linear':
                ax.plot(self.x_vals, self.y_vals)
            else:
                ax.plot(self.x_vals, self.logy_curr_data)
            self.canvas.draw()
            # after recording and displaying go to save data
            self.currState = self.state['save_data']
            self.state_machine_function()
        elif self.index > self.numberStep:
            self.message('finish measurement')
            self.index = 0
            self.started = False
            self.currState = self.state['stop']
            self.state_machine_function()

        else:
            pass

    # Real-time mode: get and plot data of real-time
    def rt_get_plot(self):
        self.message('rt get and plot')
        if self.started:
            dut_current = self.SMU.readout()
            if self.index == 0:
                self.start_time = time.time()
            self.current_time = time.time()
            time_lapsed = self.current_time - self.start_time
            # append the acquired data to the list containing data
            self.y_vals.append(dut_current)
            self.logy_curr_data.append(abs(dut_current))
            self.x_vals.append(time_lapsed)
            self.index += 1
            # plot the data in real-time
            self.figure.clear()
            # plt.tight_layout()
            ax = self.figure.add_subplot(111)
            plt.yscale(self.yscale)
            plt.autoscale(enable=True, axis='y')
            # ticklabel format
            ax.grid(which='major', color='grey', linewidth=1)
            ax.grid(which='minor', color='darkgrey', linestyle=':', linewidth=0.8)
            ax.minorticks_on()
            plt.title("Real-time measurement", fontsize=20, fontweight='bold')
            plt.xlabel("time (s)", fontsize=18, fontweight='bold')
            plt.ylabel("current (A)", fontsize=18, fontweight='bold')
            plt.rcParams['xtick.labelsize'] = 16
            plt.rcParams['ytick.labelsize'] = 16
            # plot history data
            for i in range(self.repeat):
                if self.yscale == 'linear':
                    ax.plot(self.x_alldata[i], self.y_alldata[i])
                else:
                    ax.plot(self.x_alldata[i], self.logy_all_data[i])

            # plot current data
            if self.yscale == 'linear':
                ax.plot(self.x_vals, self.y_vals)
            else:
                ax.plot(self.x_vals, self.logy_curr_data)
            self.canvas.draw()
            # after get and plot go to saver to save the data
            self.currState = self.state['save_data']
            self.state_machine_function()

        else:
            self.currState = self.state['wait_for_event']
            self.state_machine_function()

    # function to readout current I as applying voltage V
    def read_current_out(self, voltage):

        self.SMU.set_voltage_level(voltage)
        # delay 150 ms before reading the current
        # this delay time has to be higher than Source-Delay-Measurement time
        # sleep time = Source-Delay + Measure + 10 ms
        time.sleep(
            (round(self.nplc_value.currentData() * 16.67) + float(self.source_delay_time_value.text()) + 10) / 1000)

        return self.SMU.readout()

    def exit_clicked(self):
        self.currState = self.state['exit']
        self.state_machine_function()
        # pass

    '''execute function for events'''

    def starter(self):
        self.started = True
        self.index = 0
        print('went into starter')
        self.message('start')
        # clear all current IV data
        self.x_vals.clear()
        self.y_vals.clear()
        # clear all current RT data

        # clear all current log data
        self.logy_curr_data.clear()

        # convert the user interface to the value for measurements
        # need to change the self.visaResourceName to something different from the class variable
        self.visaResourceName = self.visa_name.currentText()
        # print(self.visaResourceName)
        try:
            # self.Keithley = self.rm.open_resource(self.visaResourceName)
            self.SMU.create_smu_connector(self.visaResourceName)
        except pyvisa.VisaIOError:
            self.show_popup('unable to connect to the device, pls check the connection!')
            self.currState = self.state['wait_for_event']
            self.state_machine_function()
        else:
            # reset the device
            self.SMU.reset_smu()
            # timeout in second
            self.SMU.timeout_smu(25000)
            # set the corresponding terminal
            if self.terminal_value.currentData() == 'FRON':
                self.SMU.set_front_terminal()
            elif self.terminal_value.currentData() == 'REAR':
                self.SMU.set_rear_terminal()
            else:
                pass

            if self.meas_mode == 'IV':
                self.iv_starter()
            elif self.meas_mode == 'RT':
                self.rt_starter()
            else:
                pass
            # enable and disable button accordingly if sucessful started
            if self.started:
                self.start_button.setEnabled(False)
                self.exit_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.measure_mode_combo.setEnabled(False)

    def iv_starter(self):
        print('went into iv_starter')
        self.message('iv_starter')
        # activeTerminal = Front/Rear (enum)
        self.startV = float(self.from_voltage_value.text())
        # print(self.from_voltage_value.text())
        # print(self.startV)
        self.stopV = float(self.to_voltage_value.text())
        # print(self.stopV)
        self.stepV = float(self.step_voltage_value.text())
        self.numberStep = round((self.stopV - self.startV) / self.stepV)
        if self.numberStep < 1:
            self.show_popup('please check parameters')
        # create list of voltage
        self.x_vals.clear()
        self.y_vals.clear()
        for i in range(self.numberStep + 1):
            value = self.startV + i * self.stepV
            self.listV.insert(i, value)
        # select source function VOLtage
        self.SMU.set_source_function_voltage()
        # select fixed sourcing mode for V-source, this function is only for SMU2400
        self.SMU.set_source_voltage_delay_auto_off()
        # source delay measurement (DSM) is 50 ms
        self.SMU.set_source_voltage_delay_time(float(self.source_delay_time_value.text()))
        # check one more time the float forcing type
        if self.voltage_range_combo.currentText() == 'Auto':
            self.SMU.set_voltage_range_auto_on()
        else:
            # select V-source range
            self.SMU.set_voltage_range_value(self.voltage_range_combo.currentData())
        # select V source amplitude
        self.SMU.set_voltage_level(0.0)
        # select measure function
        self.SMU.set_measure_mode_current()
        # current range = current compliance
        self.SMU.set_measure_current_range(self.current_range_combo.currentData())
        # current compliance SOUR:VOLT:ILIM 1
        self.SMU.set_measure_current_limit(self.current_range_combo.currentData())
        # nplc setting
        self.SMU.set_measure_current_nplc(self.nplc_value.currentData())
        # current reading only, only for SMU2400
        # keithley on
        self.SMU.set_output_on()

        # go to startV in 10 steps
        self.goto_voltage(self.startV, 10)

        # create file for recording here
        # program_path = os.getcwd()
        currentTime = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        file_name = 'IV' + self.file_name_text.text() + currentTime + '.txt'
        self.filepath = os.path.join(self.folder_location_text.text(), file_name)
        self.communication_text.setText(self.filepath)

        # only start measuring if the file can be opened
        try:
            self.f = open(self.filepath, "w")
        except OSError as e:
            # print('can not open/create file in the location', e)
            self.show_popup('can not open/create file in the location')
            self.started = False
        else:
            self.f.write('voltage' + '\t' + 'current' + '\n')

            # start timer here
            time_out = round(self.nplc_value.currentData() * 16.67) + round(
                float(self.source_delay_time_value.text())) + 50
            self.timer_function(time_out)

        # set the next state to wait for event
        self.currState = self.state['wait_for_event']
        self.state_machine_function()

    def rt_starter(self):
        # print('rt_starter get in')
        # clear current value
        # self.Keithley.write(':SOUR:FUNC VOLT')
        self.SMU.set_source_function_voltage()
        # select fixed soucrcing mode for V-source, this function is only for SMU2400
        # source delay measurement (DSM) is automatic in the real-time case
        self.SMU.set_source_voltage_delay_auto_on()

        if self.rt_voltage_range_combo.currentText() == 'Auto':
            # self.Keithley.write(":SOUR:VOLT:RANG:AUTO 1")
            self.SMU.set_voltage_range_auto_on()
        else:
            # select V-source range
            self.SMU.set_voltage_range_value(self.rt_voltage_range_combo.currentData())
        # select V source amplitude
        self.SMU.set_voltage_level(self.rt_voltage_set_value.text())
        # select measure function
        self.SMU.set_measure_mode_current()
        self.SMU.set_measure_current_limit(self.rt_current_range_combo.currentData())
        # current range = current compliance
        self.SMU.set_measure_current_range(self.rt_current_range_combo.currentData())
        # nplc setting
        self.SMU.set_measure_current_nplc(self.nplc_value.currentData())
        # current reading only, this function is only for SMU2400
        # keithley on
        self.SMU.set_output_on()
        # to to the rt_voltage_set_value in 10 steps
        if self.repeat == 0:
            self.goto_voltage(float(self.rt_voltage_set_value.text()), 10)
        else:
            self.SMU.set_voltage_level(self.rt_voltage_set_value.text())
            time.sleep(0.05)

        # open or create a file
        currentTime = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        file_name = 'RT' + self.file_name_text.text() + currentTime + '.txt'
        self.filepath = os.path.join(self.folder_location_text.text(), file_name)

        try:
            self.f = open(self.filepath, "w")
        except OSError as e:
            # print('can not open/create file in the location', e)
            self.show_popup('can not open/create file in the location')
            self.started = False
        else:
            self.f.write('time' + '\t' + 'current' + '\n')
            # start the time
            self.start_time = time.time()
            # print(f'start_time : {self.start_time}')
            # start the timer for rt measurement here
            self.timer_function(round(float(self.rt_aperture_value.text()) * 1000))

        # set the next state to wait for event
        # after initialization of the device goes to wait_for_event
        self.currState = self.state['wait_for_event']
        self.state_machine_function()

    def goto_voltage(self, set_voltage, num_step):
        # the device was already connected and ready for command
        # jump the output to the set_voltage from 0
        delta_voltage = set_voltage / num_step
        for i in range(num_step + 1):
            output_voltage = i * delta_voltage
            self.SMU.set_voltage_level(output_voltage)
            # sleep time = delay some ms for the voltage to jump to the value
            time.sleep(0.01)
            self.SMU.readout()

    def stoper(self):
        # print('do stoper and close file')
        self.message('stop')
        # stop timer_function
        if self.timer.isActive():
            self.timer.stop()
        # close the file if not closed
        if not self.f.closed:
            self.f.close()

        self.SMU.reset_smu()
        self.SMU.set_output_off()
        self.SMU.close_smu()
        self.started = False
        # increase the repeat time to +1
        self.repeat += 1

        # append current data to the all data
        self.x_alldata.append(self.x_vals.copy())
        self.y_alldata.append(self.y_vals.copy())
        self.logy_all_data.append(self.logy_curr_data.copy())

        # enable and disable buttons
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.exit_button.setEnabled(True)
        self.measure_mode_combo.setEnabled(True)

        # go back to wait_for_event
        self.currState = self.state['wait_for_event']
        self.state_machine_function()
        # return True
        self.timer.stop()

    def exiter(self):
        # print('exiter')
        self.message('exit')
        # make sure click stop if started before clicking exit
        self.currState = self.state['exit']

        if self.SMU:
            self.SMU.close_smu()
        self.close()
        # return True

    def default(self):
        print('no such command existed')
        # return False

    def waiter(self):
        pass

    def saver(self):
        self.message('saver')
        if self.meas_mode == 'IV' and self.save_data:
            # print('inside save function')
            save_data = str(self.currentV) + '\t' + str(self.currentI) + '\n'
            self.f.write(save_data)
            # after saving jump to 'wait_for_event'
            self.currState = self.state['wait_for_event']
            self.state_machine_function()
        elif self.meas_mode == 'RT' and self.save_data:
            # save data in rt mode
            save_data = str(self.x_vals[-1]) + '\t' + str(self.y_vals[-1]) + '\n'
            self.f.write(save_data)
            # after saving jump to wait_for_event
            self.currState = self.state['wait_for_event']
            self.state_machine_function()

    '''dictionary and switch function for state-machine'''

    def switch(self, currentState):
        return self.switcher.get(currentState, self.default)()

    # state machine
    def state_machine_function(self):
        print(f"go to state_machine_function, current state: {self.currState}")
        self.switch(self.currState)

    def show_popup(self, msg):
        msg_window = qtw.QMessageBox()
        msg_window.setWindowTitle('Message')
        msg_window.setText(msg)
        msg_window.exec_()

    def message(self, msg):
        # message = str(msg)
        message = f'save location: {self.filepath} \nstate: {msg}'
        self.communication_text.setText(message)

    def closeEvent(self, event):
        # windows position and size
        self.setting_window.setValue('window_size', self.size())
        self.setting_window.setValue('window_position', self.pos())

        # user interface parameters
        self.setting_variable.setValue('visa_name', self.visa_name.currentText())
        self.setting_variable.setValue('terminal', self.terminal_value.currentText())
        self.setting_variable.setValue('nplc', self.nplc_value.currentText())
        self.setting_variable.setValue('mea_mode', self.measure_mode_combo.currentText())
        #
        # # IV Parameters
        self.setting_variable.setValue('sour_delay_time', self.source_delay_time_value.text())
        self.setting_variable.setValue('v_range', self.voltage_range_combo.currentText())
        self.setting_variable.setValue('from_v', self.from_voltage_value.text())
        self.setting_variable.setValue('to_v', self.to_voltage_value.text())
        self.setting_variable.setValue('step_v', self.step_voltage_value.text())
        self.setting_variable.setValue('i_range', self.current_range_combo.currentText())

        # # RT parameters
        self.setting_variable.setValue('rt_v_range', self.rt_voltage_range_combo.currentText())
        self.setting_variable.setValue('rt_v_set', self.rt_voltage_set_value.text())
        self.setting_variable.setValue('rt_i_range', self.rt_current_range_combo.currentText())
        self.setting_variable.setValue('aperture', self.rt_aperture_value.text())
        #
        # # file and Plot Dialog
        self.setting_variable.setValue('save_folder', self.folder_location_text.text())
        self.setting_variable.setValue('file_name', self.file_name_text.text())
        self.setting_variable.setValue('y_scale', self.log_linear_combo.currentText())
