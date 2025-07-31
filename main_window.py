from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from view.view import View
from view.components.config_dialog import ConfigDialog
from devices.smu_simulation import SMUSimulation 
import pyvisa
import time
import os
import datetime
import matplotlib.pyplot as plt

class MainWindow(qtw.QWidget):
    def __init__(self):    
        super().__init__()

        self.config = {
            'IV': {
                'source_delay_ms': 50,
                'voltage_range': 2.0,
                'startV': -1.0,
                'stopV': 1.0,
                'stepV': 0.1,
                'current_range': 1e-6                
            },
            'RT': {
                'rt_voltage_range': 2.0,
                'rt_voltage_set': 0.5,
                'rt_current_range': 1e-6,
                'rt_aperture': 1.0

            },
            'global': {
                'visa_name': 'GPIB1::1::INSTR',
                'terminal': 'FRONT',
                'nplc': 1.0,
                'meas_mode': 'IV',
                'save_folder': os.path.join(os.getcwd(), 'data'),
                'file_name': 'data',
                'y_scale': 'linear'              
            }
        }

        self.view = View()
        self.settings_init()
        self.connect_signals()
        self.view.show()

        # data to implement measurement logic
        self.filepath = None
        self.SMU = SMUSimulation()
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
        # file for recording
        self.f = None
        # graph display mode  

        self.numberStep = round((self.config['IV']['stopV'] - self.config['IV']['startV']) / self.config['IV']['stepV'])

        # list of voltage that will be applied to the device
        self.listV = []
        self.currentV = None
        self.currentI = None
        # create instance for connecting to the device
        self.rm = pyvisa.ResourceManager()
        # messge for the user

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
    
    def switch(self, currentState):
        return self.switcher.get(currentState, self.default)()
    
    def state_machine_function(self):
        self.switch(self.currState)

    def software_version(self):
        self.software_version = {'free': 0,
                                 'limited': 1,
                                 'unlimited': 2}
        # self.sw_version = self.software_version['free']
        self.sw_version = self.software_version['unlimited']
        self.MAC_list = ['34:73:5a:d3:37:32', # Dell personal Labtop
                         'e4:54:e8:58:4f:9e' # office computer
                         ]
    def settings_init(self):
        self.setting_window = qtc.QSettings('KeithleyIV_RT', 'windows size')
        self.setting_variable = qtc.QSettings('KeithleyIV_RT', 'user interface')
        self.timer = qtc.QTimer()
        self.timer.timeout.connect(self.timeOutEvent)
        # load saved settings into the view
        self.view.load_settings(self.setting_window, self.setting_variable)

    def connect_signals(self):
        # Connect signals to slots here
        self.view.configure_button.clicked.connect(self.open_config_dialog)
        self.view.start_button.clicked.connect(self.start_clicked)
        self.view.stop_button.clicked.connect(self.stop_clicked)
        self.view.exit_button.clicked.connect(self.exit_clicked)

        # measurement mode change
        # self.view.measure_mode_combo.activated.connect(self.measure_mode_changed)
        # search folder button
        # self.view.search_folder_button.clicked.connect(self.folder_clicked)
        # clear graph button
        self.view.clear_graph_button.clicked.connect(self.clear_graph_clicked)

        # Connect close event
        self.view.closeSignal.connect(self.on_view_closed)
    # open configuration dialog
    def open_config_dialog(self):
        # call ConfigDiaglog
        dialog = ConfigDialog(self.config, parent=self)
        if dialog.exec_():
            updated_config = dialog.get_config()
            self.config['IV'].update(updated_config['IV'])
            self.config['RT'].update(updated_config['RT'])
            self.config['global'].update(updated_config['global'])
            print("[MainWindow] Config updated:", self.config)
            # clear measurement data after updating config
            self.clear_data()
    
    # update data from View
    def update_config_from_view(self):

        self.config['global']['visa_name'] = self.view.visa_name.currentText()
        self.config['global']['terminal'] = self.view.terminal_value.currentData()
        self.config['global']['nplc'] = float(self.view.nplc_value.currentData())
        # self.config['global']['meas_mode'] = self.view.measure_mode_combo.currentText()

        self.config['global']['save_folder'] = self.view.folder_location_text.text()
        self.config['global']['file_name'] = self.view.file_name_text.text()
        self.config['global']['y_scale'] = self.view.log_linear_combo.currentText()        

        self.config['IV']['source_delay_ms'] = float(self.view.source_delay_time_value.text())
        self.config['IV']['voltage_range'] = float(self.view.voltage_range_combo.currentData())
        self.config['IV']['startV'] = float(self.view.from_voltage_value.text())
        self.config['IV']['stopV'] = float(self.view.to_voltage_value.text())
        self.config['IV']['stepV'] = float(self.view.step_voltage_value.text())
        self.config['IV']['current_range'] = float(self.view.current_range_combo.currentData())
        
        self.config['RT']['rt_voltage_range'] = float(self.view.rt_voltage_range_combo.currentData())
        self.config['RT']['rt_voltage_set'] = float(self.view.rt_voltage_set_value.text())
        self.config['RT']['rt_current_range'] = float(self.view.rt_current_range_combo.currentData())
        self.config['RT']['rt_aperture'] = float(self.view.rt_aperture_value.text())
        
    def timer_function(self, time_out):
        self.timer.start(time_out)
        # call the timeOutEvent function directly after iv/rt_starter
        self.timeOutEvent()

    def timeOutEvent(self):
        if self.config['global']['meas_mode'] == 'IV':
            self.iv_get_plot()
        elif self.config['global']['meas_mode'] == 'RT':
            self.rt_get_plot()
        else:
            pass
    
     # get and plot data in IV mode
    def iv_get_plot(self):
        self.view.message('iv get and plot')
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
            self.view.figure.clear()
            ax = self.view.figure.add_subplot(1, 1, 1)
            plt.yscale(self.config['global']['y_scale'])
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
                if self.config['global']['y_scale'] == 'linear':
                    ax.plot(self.x_alldata[i], self.y_alldata[i])
                else:
                    # plot log data if in log scale
                    ax.plot(self.x_alldata[i], self.logy_all_data[i])
            # plot current data
            if self.config['global']['y_scale'] == 'linear':
                ax.plot(self.x_vals, self.y_vals)
            else:
                ax.plot(self.x_vals, self.logy_curr_data)
            self.view.canvas.draw()
            # after recording and displaying go to save data
            self.currState = self.state['save_data']
            self.state_machine_function()
        elif self.index > self.numberStep:
            self.view.message('finish measurement')
            self.index = 0
            self.started = False
            self.currState = self.state['stop']
            self.state_machine_function()

        else:
            pass

    # Real-time mode: get and plot data of real-time
    def rt_get_plot(self):
        self.view.message('rt get and plot')
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
            self.view.figure.clear()
            # plt.tight_layout()
            ax = self.view.figure.add_subplot(111)
            plt.yscale(self.config['global']['y_scale'])
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
                if self.config['global']['y_scale'] == 'linear':
                    ax.plot(self.x_alldata[i], self.y_alldata[i])
                else:
                    ax.plot(self.x_alldata[i], self.logy_all_data[i])

            # plot current data
            if self.config['global']['y_scale'] == 'linear':
                ax.plot(self.x_vals, self.y_vals)
            else:
                ax.plot(self.x_vals, self.logy_curr_data)
            self.view.canvas.draw()
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
            (round(self.config['global']['nplc'] * 16.67) + self.config['IV']['source_delay_ms'] + 10) / 1000)

        return self.SMU.readout()
    
    def initializer(self):
        self.view.message("Initializing...")
        # maybe load user settings here
        # enable View buttons
        self.view.start_button.setEnabled(True)
        self.view.stop_button.setEnabled(False)
        self.view.exit_button.setEnabled(True)
        # self.view.measure_mode_combo.setEnabled(True)
        self.save_data = True
        # set the current state
        self.currState = self.state['wait_for_event']

    def start_clicked(self):
        self.currState = self.state['start']
        self.view.message("Start button clicked")
        # implement starter
        self.state_machine_function()

    def stop_clicked(self):
        self.currState = self.state['stop']
        self.view.message("Stop button clicked")
        self.state_machine_function()

    # def folder_clicked(self):
    #     currentLocation = qtw.QFileDialog.getExistingDirectory(
    #         self,
    #         caption='select a folder',
    #         directory=os.getcwd()
    #     )
    #     self.view.folder_location_text.setText(currentLocation)

    def exit_clicked(self):
        # Exit button logic
        self.currState = self.state['exit']
        self.state_machine_function()
    
    def measure_mode_changed(self):
        # self.config['global']['meas_mode'] = self.view.measure_mode_combo.currentText()
        # change the mode, the repeat value set back to 0

        self.clear_data()

        self.view.message(self.config['global']['meas_mode'])
        # self.view.tabs_IV_RT.setCurrentIndex(self.view.measure_mode_combo.currentData())

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

    def clear_graph_clicked(self):
        # Clear graph logic
        print("Clear graph button clicked")

    def on_view_closed(self):
        self.view.save_settings(self.setting_window, self.setting_variable)
        self.view.close()
        print("MainView closed")
        
    '''excecute function for events'''
    def starter(self):
        self.started = True
        self.index = 0
        print('went into starter')
        self.view.message('start')
        # clear all current IV data
        self.x_vals.clear()
        self.y_vals.clear()
        # clear all current RT data

        # clear all current log data
        self.logy_curr_data.clear()

        # update all config from the view
        # self.update_config_from_view()

        # convert the user interface to the value for measurements

        try:
            self.SMU.create_smu_connector(self.config['global']['visa_name'])
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
            if self.config['global']['terminal'] == 'FRON':
                self.SMU.set_front_terminal()
            elif self.config['global']['terminal'] == 'REAR':
                self.SMU.set_rear_terminal()
            else:
                pass

            if self.config['global']['meas_mode'] == 'IV':
                self.iv_starter()
            elif self.config['global']['meas_mode'] == 'RT':
                self.rt_starter()
            else:
                pass
            # enable and disable button accordingly if sucessful started
            if self.started:
                self.view.start_button.setEnabled(False)
                self.view.exit_button.setEnabled(False)
                self.view.stop_button.setEnabled(True)
                # self.view.measure_mode_combo.setEnabled(False)
    def iv_starter(self):
        print('went into iv_starter')
        self.view.message('iv_starter')
        # activeTerminal = Front/Rear (enum)
        self.numberStep = round((self.config['IV']['stopV'] - self.config['IV']['startV']) / self.config['IV']['stepV'])
        if self.numberStep < 1:
            self.show_popup('please check parameters')
        # create list of voltage
        self.x_vals.clear()
        self.y_vals.clear()
        for i in range(self.numberStep + 1):
            value = self.config['IV']['startV'] + i * self.config['IV']['stepV']
            self.listV.insert(i, value)
        # select source function VOLtage
        self.SMU.set_source_function_voltage()
        # select fixed sourcing mode for V-source, this function is only for SMU2400
        self.SMU.set_source_voltage_delay_auto_off()
        # source delay measurement (DSM) is 50 ms
        self.SMU.set_source_voltage_delay_time(self.config['IV']['source_delay_ms'])
        # check one more time the float forcing type
        # better to compare text than the currentData == 0
        if self.config['IV']['voltage_range'] == 0:
            self.SMU.set_voltage_range_auto_on()
        else:
            # select V-source range
            self.SMU.set_voltage_range_value(self.config['IV']['voltage_range'])
        # select V source amplitude
        self.SMU.set_voltage_level(0.0)
        # select measure function
        self.SMU.set_measure_mode_current()
        # current range = current compliance
        self.SMU.set_measure_current_range(self.config['IV']['current_range'])
        # current compliance SOUR:VOLT:ILIM 1
        self.SMU.set_measure_current_limit(self.config['IV']['current_range'])
        # nplc setting
        self.SMU.set_measure_current_nplc(self.config['global']['nplc'])
        # current reading only, only for SMU2400
        # keithley on
        self.SMU.set_output_on()

        # go to startV in 10 steps
        self.goto_voltage(self.config['IV']['startV'], 10)

        # create file for recording here
        # program_path = os.getcwd()
        currentTime = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        file_name = 'IV' + self.config['global']['file_name'] + currentTime + '.txt'
        self.filepath = os.path.join(self.config['global']['save_folder'], file_name)
        self.view.communication_text.setText(self.filepath)

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
            time_out = round(self.config['global']['nplc'] * 16.67) + round(
                self.config['IV']['source_delay_ms']) + 50
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

        if self.config['RT']['rt_voltage_range'] == 'Auto':
            # self.Keithley.write(":SOUR:VOLT:RANG:AUTO 1")
            self.SMU.set_voltage_range_auto_on()
        else:
            # select V-source range
            self.SMU.set_voltage_range_value(self.config['RT']['rt_voltage_range'])
        # select V source amplitude
        self.SMU.set_voltage_level(self.config['RT']['rt_voltage_set'])
        # select measure function
        self.SMU.set_measure_mode_current()
        self.SMU.set_measure_current_limit(self.config['RT']['rt_current_range'])
        # current range = current compliance
        self.SMU.set_measure_current_range(self.config['RT']['rt_current_range'])
        # nplc setting
        self.SMU.set_measure_current_nplc(self.config['global']['nplc'])
        # current reading only, this function is only for SMU2400
        # keithley on
        self.SMU.set_output_on()
        # to to the rt_voltage_set_value in 10 steps
        if self.repeat == 0:
            self.goto_voltage(self.config['RT']['rt_voltage_set'], 10)
        else:
            self.SMU.set_voltage_level(self.config['RT']['rt_voltage_set'])
            time.sleep(0.05)

        # open or create a file
        currentTime = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        file_name = 'RT' + self.config['global']['file_name'] + currentTime + '.txt'
        self.filepath = os.path.join(self.config['global']['save_folder'], file_name)

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
            self.timer_function(round(self.config['RT']['rt_aperture'] * 1000))

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
        self.view.message('stop')
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
        self.view.start_button.setEnabled(True)
        self.view.stop_button.setEnabled(False)
        self.view.exit_button.setEnabled(True)
        # self.view.measure_mode_combo.setEnabled(True)

        # go back to wait_for_event
        self.currState = self.state['wait_for_event']
        self.state_machine_function()
        # return True
        self.timer.stop()

    def exiter(self):
        # print('exiter')
        self.view.message('exit')
        # make sure click stop if started before clicking exit
        self.currState = self.state['exit']

        if self.SMU:
            self.SMU.close_smu()
        self.on_view_closed()
        # return True

    def waiter(self):
        pass

    def saver(self):
        self.view.message('saver')
        if self.config['global']['meas_mode'] == 'IV' and self.save_data:
            # print('inside save function')
            save_data = str(self.currentV) + '\t' + str(self.currentI) + '\n'
            self.f.write(save_data)
            # after saving jump to 'wait_for_event'
            self.currState = self.state['wait_for_event']
            self.state_machine_function()
        elif self.config['global']['meas_mode'] == 'RT' and self.save_data:
            # save data in rt mode
            save_data = str(self.x_vals[-1]) + '\t' + str(self.y_vals[-1]) + '\n'
            self.f.write(save_data)
            # after saving jump to wait_for_event
            self.currState = self.state['wait_for_event']
            self.state_machine_function()

    def default(self):
        print('no such command existed')
        # return False
    
    def show_popup(self, msg):
        msg_window = qtw.QMessageBox()
        msg_window.setWindowTitle('Message')
        msg_window.setText(msg)
        msg_window.exec_()    

    