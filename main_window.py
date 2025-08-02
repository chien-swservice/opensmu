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
import json
import sys

class MainWindow(qtw.QWidget):
    def __init__(self):    
        super().__init__()
        self._init_config()
        self._init_ui()
        self._init_measurement_data()
        self._init_state_machine()
        self._setup_initial_state()
    
    def _init_config(self):
        """Initialize default configuration"""
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
    
    def _init_ui(self):
        """Initialize UI components"""
        self.view = View()
        self.settings_init()
        self.load_config()
        self.connect_signals()
        self.view.show()
    
    def _init_measurement_data(self):
        """Initialize measurement data structures"""
        self.filepath = None
        self.SMU = SMUSimulation()
        self.started = False
        
        # Time variables
        self.start_time = time.time()
        self.current_time = time.time()
        
        # Plot data
        self.logy_curr_data = []
        self.logy_all_data = []
        self.x_alldata = []
        self.y_alldata = []
        self.repeat = 0
        
        # Current measurement data
        self.x_vals = []
        self.y_vals = []
        self.index = 0
        self.f = None
        
        # Voltage list for IV measurements
        self.listV = []
        self.currentV = None
        self.currentI = None
        
        # Calculate number of steps for IV measurements
        self.numberStep = round((self.config['IV']['stopV'] - self.config['IV']['startV']) / self.config['IV']['stepV'])
        
        # Track measurement mode for clearing logic
        self.last_meas_mode = self.config['global']['meas_mode']
    
    def _init_state_machine(self):
        """Initialize state machine"""
        self.state = {
            'initialize': 0,
            'wait_for_event': 1,
            'start': 2,
            'stop': 3,
            'exit': 4,
            'save_data': 5
        }
        self.currState = self.state['initialize']
        
        self.switcher = {
            self.state['initialize']: self.initializer,
            self.state['start']: self.starter,
            self.state['stop']: self.stoper,
            self.state['exit']: self.exiter,
            self.state['wait_for_event']: self.waiter,
            self.state['save_data']: self.saver
        }
    
    def _setup_initial_state(self):
        """Setup initial state and start state machine"""
        self.state_machine_function()
    
    def switch(self, currentState):
        """State machine switch function"""
        return self.switcher.get(currentState, self.default)()
    
    def state_machine_function(self):
        """Execute current state"""
        print("DEBUG: state_machine_function called!")
        print("current state: " + str(self.currState))
        sys.stdout.flush()
        self.switch(self.currState)
    
    def settings_init(self):
        """Initialize settings and timer"""
        self.setting_window = qtc.QSettings('KeithleyIV_RT', 'windows size')
        self.timer = qtc.QTimer()
        self.timer.timeout.connect(self.timeOutEvent)
        self.view.load_settings(self.setting_window)
    
    def connect_signals(self):
        """Connect all UI signals"""
        self.view.start_button.clicked.connect(self.start_clicked)
        self.view.stop_button.clicked.connect(self.stop_clicked)
        self.view.exit_button.clicked.connect(self.exit_clicked)
    
        self.view.configure_button.clicked.connect(self.open_config_dialog)
        self.view.destroyed.connect(self.on_view_closed)
        self.view.clear_graph_button.clicked.connect(self.clear_graph_clicked)
        self.view.closeSignal.connect(self.on_view_closed)
    
    def open_config_dialog(self):
        dialog = ConfigDialog(self.config, parent=self)
        if dialog.exec_():
            updated_config = dialog.get_config()
            self.config['IV'].update(updated_config['IV'])
            self.config['RT'].update(updated_config['RT'])
            self.config['global'].update(updated_config['global'])
            print("[MainWindow] Config updated:", self.config)
            # save configuration after updating
            self.save_config()
            self.apply_config_to_view()
    
    def timer_function(self, time_out):
        """Start timer with specified timeout"""
        self.timer.start(int(time_out))
    
    def timeOutEvent(self):
        """Handle timer timeout event"""
        print("go to main_window timeOutEvent")
        if self.config['global']['meas_mode'] == 'IV':
            self.iv_get_plot()
        elif self.config['global']['meas_mode'] == 'RT':
            self.rt_get_plot()
    
    def _setup_smu_connection(self):
        """Setup SMU connection with error handling"""
        try:
            self.SMU.create_smu_connector(self.config['global']['visa_name'])
            return True
        except pyvisa.VisaIOError:
            self.show_popup('Unable to connect to the device, please check the connection!')
            self.currState = self.state['wait_for_event']
            self.state_machine_function()
            return False
    
    def _configure_smu_basic(self):
        """Configure basic SMU settings"""
        self.SMU.reset_smu()
        self.SMU.timeout_smu(25000)
        
        # Set terminal
        if self.config['global']['terminal'] == 'FRON':
            self.SMU.set_front_terminal()
        elif self.config['global']['terminal'] == 'REAR':
            self.SMU.set_rear_terminal()
    
    def _configure_voltage_source(self, voltage_range, voltage_level):
        """Configure voltage source settings"""
        self.SMU.set_source_function_voltage()
        
        if voltage_range == 0:
            self.SMU.set_voltage_range_auto_on()
        else:
            self.SMU.set_voltage_range_value(voltage_range)
        
        self.SMU.set_voltage_level(voltage_level)
    
    def _configure_current_measurement(self, current_range):
        """Configure current measurement settings"""
        self.SMU.set_measure_mode_current()
        self.SMU.set_measure_current_range(current_range)
        self.SMU.set_measure_current_limit(current_range)
        self.SMU.set_measure_current_nplc(self.config['global']['nplc'])
    
    def _create_data_file(self, mode_prefix):
        """Create data file for measurements"""
        currentTime = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        file_name = f'{mode_prefix}{self.config["global"]["file_name"]}{currentTime}.txt'
        self.filepath = os.path.join(self.config['global']['save_folder'], file_name)
        self.view.communication_text.setText(self.filepath)
        
        try:
            self.f = open(self.filepath, "w")
            return True
        except OSError:
            self.show_popup('Cannot open/create file in the location')
            self.started = False
            return False
    
    def _update_button_states(self, start_enabled=True, stop_enabled=False, exit_enabled=True):
        """Update button states"""
        self.view.start_button.setEnabled(start_enabled)
        self.view.stop_button.setEnabled(stop_enabled)
        self.view.exit_button.setEnabled(exit_enabled)
    
    def _clear_current_data(self):
        """Clear current measurement data"""
        self.x_vals.clear()
        self.y_vals.clear()
        self.logy_curr_data.clear()
    
    def iv_get_plot(self):
        """Handle IV measurement plotting"""
        if self.index < len(self.listV):
            voltage = self.listV[self.index]
            current = self.read_current_out(voltage)
            
            self.x_vals.append(voltage)
            self.y_vals.append(current)
            self.logy_curr_data.append(abs(current))
            
            # Write to file
            if self.f and not self.f.closed:
                self.f.write(f'{voltage}\t{current}\n')
                self.f.flush()
            
            # Update plot
            self.view.plot_iv(self.x_vals, self.y_vals, self.config['global']['y_scale'], 
                             self.x_alldata, self.y_alldata)
            
            self.index += 1
            
            # Continue measurement if not finished
            if self.index >= len(self.listV):
                # Measurement complete
                self.currState = self.state['save_data']
                self.state_machine_function()
        else:
            self.currState = self.state['save_data']
            self.state_machine_function()
    
    def rt_get_plot(self):
        """Handle RT measurement plotting"""
        print("go to main_window rt_get_plot")
        current = self.SMU.readout()
        current_time = time.time() - self.start_time
        
        self.x_vals.append(current_time)
        self.y_vals.append(current)
        
        # Write to file
        if self.f and not self.f.closed:
            self.f.write(f'{current_time}\t{current}\n')
            self.f.flush()
        
        # Update plot
        
        self.view.plot_rt(self.x_vals, self.y_vals, self.config['global']['y_scale'], 
                          self.x_alldata, self.y_alldata, self.repeat)
    
    def read_current_out(self, voltage):
        """Read current output for given voltage"""
        self.SMU.set_voltage_level(voltage)
        time.sleep(self.config['IV']['source_delay_ms'] / 1000.0)
        return self.SMU.readout()
    
    def initializer(self):
        """Initialize state"""
        self.currState = self.state['wait_for_event']
        self.state_machine_function()
    
    def start_clicked(self):
        """Handle start button click"""
        self.currState = self.state['start']
        print("start_clicked") # debug
        self.state_machine_function()
    
    def stop_clicked(self):
        """Handle stop button click"""
        self.currState = self.state['stop']
        self.state_machine_function()
    
    def exit_clicked(self):
        """Handle exit button click"""
        self.currState = self.state['exit']
        self.state_machine_function()
    
    def clear_data(self):
        """Clear all measurement data"""
        self.x_alldata.clear()
        self.y_alldata.clear()
        self.logy_all_data.clear()
        self._clear_current_data()
        self.view.clear_plot()
        # Reset measurement mode tracking to force clear on next start
        self.last_meas_mode = None
    
    def clear_graph_clicked(self):
        """Handle clear graph button click"""
        self.clear_data()
    
    def on_view_closed(self):
        """Handle view close event"""
        self.save_config()
        self.view.save_settings(self.setting_window)
        self.view.close()
        print("MainView closed")
    
    def starter(self):
        """Start measurement process"""
        self.started = True
        self.index = 0
        print('Started measurement')
        self.view.message('start')
        
        # Only clear data if measurement mode changed
        if hasattr(self, 'last_meas_mode') and self.last_meas_mode != self.config['global']['meas_mode']:
            self.clear_data()  # Clear all data including historical data
        
        # Store current measurement mode
        self.last_meas_mode = self.config['global']['meas_mode']
        
        if not self._setup_smu_connection():
            return
        
        self._configure_smu_basic()
        
        if self.config['global']['meas_mode'] == 'IV':
            self.iv_starter()
        elif self.config['global']['meas_mode'] == 'RT':
            self.rt_starter()
        
        if self.started:
            self._update_button_states(start_enabled=False, stop_enabled=True, exit_enabled=False)
    
    def iv_starter(self):
        """Start IV measurement"""
        print('Starting IV measurement')
        self.view.message('iv_starter')
        
        self.numberStep = round((self.config['IV']['stopV'] - self.config['IV']['startV']) / self.config['IV']['stepV'])
        if self.numberStep < 1:
            self.show_popup('Please check parameters')
            return
        
        # Create voltage list
        self.x_vals.clear()
        self.y_vals.clear()
        self.listV.clear()
        for i in range(self.numberStep + 1):
            value = self.config['IV']['startV'] + i * self.config['IV']['stepV']
            self.listV.append(value)
        
        # Configure SMU for IV measurement
        self._configure_voltage_source(self.config['IV']['voltage_range'], 0.0)
        self.SMU.set_source_voltage_delay_auto_off()
        self.SMU.set_source_voltage_delay_time(self.config['IV']['source_delay_ms'])
        self._configure_current_measurement(self.config['IV']['current_range'])
        self.SMU.set_output_on()
        
        # Go to start voltage
        self.goto_voltage(self.config['IV']['startV'], 10)
        
        # Create data file
        if not self._create_data_file('IV'):
            return
        
        # Write header to file
        self.f.write('voltage\tcurrent\n')
        
        # Start timer for IV measurement
        # Calculate timeout based on NPLC and source delay
        timeout = int(round(self.config['global']['nplc'] * 16.67) + self.config['IV']['source_delay_ms'] + 50)
        self.timer_function(timeout)
        
        # Start measurement
        self.currState = self.state['wait_for_event']
        self.state_machine_function()
    
    def rt_starter(self):
        """Start RT measurement"""
        print('Starting RT measurement')
        self.view.message('rt_starter')
        
        # Configure SMU for RT measurement
        self._configure_voltage_source(self.config['RT']['rt_voltage_range'], self.config['RT']['rt_voltage_set'])
        self.SMU.set_source_voltage_delay_auto_on()
        self._configure_current_measurement(self.config['RT']['rt_current_range'])
        self.SMU.set_output_on()
        
        # Go to voltage set point
        if self.repeat == 0:
            self.goto_voltage(self.config['RT']['rt_voltage_set'], 10)
        else:
            self.SMU.set_voltage_level(self.config['RT']['rt_voltage_set'])
            time.sleep(0.05)
        
        # Create data file
        if not self._create_data_file('RT'):
            return
        
        # Write header and start measurement
        self.f.write('time\tcurrent\n')
        self.start_time = time.time()
        
        # Reset current data for new measurement run
        self._clear_current_data()
        
        self.timer_function(int(round(self.config['RT']['rt_aperture'] * 1000)))
        
        self.currState = self.state['wait_for_event']
        self.state_machine_function()
    
    def goto_voltage(self, set_voltage, num_step):
        """Gradually increase voltage to target value"""
        delta_voltage = set_voltage / num_step
        for i in range(num_step + 1):
            output_voltage = i * delta_voltage
            self.SMU.set_voltage_level(output_voltage)
            time.sleep(0.01)
            self.SMU.readout()
    
    def stoper(self):
        """Stop measurement process"""
        self.view.message('stop')
        
        # Stop timer
        if self.timer.isActive():
            self.timer.stop()
        
        # Close file
        if self.f and not self.f.closed:
            self.f.close()
        
        # Reset SMU
        self.SMU.reset_smu()
        self.SMU.set_output_off()
        self.SMU.close_smu()
        self.started = False
        self.repeat += 1
        
        # Save current data
        self.x_alldata.append(self.x_vals.copy())
        self.y_alldata.append(self.y_vals.copy())
        self.logy_all_data.append(self.logy_curr_data.copy())
        
        # Update button states
        self._update_button_states()
        
        # Return to wait state
        self.currState = self.state['wait_for_event']
        self.state_machine_function()
    
    def exiter(self):
        """Exit application"""
        self.view.message('exit')
        if self.started:
            self.currState = self.state['stop']
            self.state_machine_function()
        else:
            self.view.close()
    
    def waiter(self):
        """Wait state - do nothing for 10ms"""
        print("go to main_window waiter")

    
    def saver(self):
        """Save data state"""
        if self.f and not self.f.closed:
            self.f.close()
        
        self.currState = self.state['stop']
        self.state_machine_function()
    
    def default(self):
        """Default state handler"""
        print("Unknown state")
    
    def show_popup(self, msg):
        """Show popup message"""
        qtw.QMessageBox.information(self, "Information", msg)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            with open('config/config.json', 'r') as f:
                self.config = json.load(f)
                print("Configuration loaded from config/config.json")
                self.apply_config_to_view()
        except FileNotFoundError:
            print("config/config.json not found. Using default configuration.")
        except json.JSONDecodeError:
            print("Error decoding config/config.json. Using default configuration.")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open('config/config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
                print("Configuration saved to config/config.json")
        except Exception as e:
            print(f"Error saving config/config.json: {e}")
    
    def apply_config_to_view(self):
        """Apply configuration to view components"""
        # This method can be implemented to update view components with config values
        pass