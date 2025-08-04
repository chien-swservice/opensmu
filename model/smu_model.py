"""
SMU Model - Business logic for SMU operations
"""
import time
import os
import datetime
import json
import pyvisa
from typing import Dict, Any, Optional, Tuple, List
from devices.smu_simulation import SMUSimulation
from devices.keithley2450 import keithley_2450
from devices.keithley2611 import keithley_2611
from devices.keithley26xxab import keithley_26xxab
from devices.keithley24xx import keithley_24xx
from devices.agilent_b2900 import agilent_b2900
from .measurement_data import MeasurementData


class SMUModel:
    """Model class for SMU operations - handles all business logic"""
    
    def __init__(self):
        """Initialize the SMU model"""
        self.config = self._init_default_config()
        self.data = MeasurementData()
        self.SMU = self._create_smu_instance()
        self.started = False
        self.last_meas_mode = self.config['global']['meas_mode']
        
        # State machine
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
    
    def _init_default_config(self) -> Dict[str, Any]:
        """Initialize default configuration"""
        return {
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
                'smu_type': 'simulation',
                'visa_name': 'GPIB1::1::INSTR',
                'terminal': 'FRONT',
                'nplc': 1.0,
                'meas_mode': 'IV',
                'save_folder': os.path.join(os.getcwd(), 'data'),
                'file_name': 'data',
                'y_scale': 'linear'              
            }
        }
    
    def _create_smu_instance(self):
        """Create SMU instance based on configuration"""
        smu_type = self.config['global'].get('smu_type', 'simulation')
        if smu_type == 'keithley2450':
            return keithley_2450()
        elif smu_type == 'keithley2611':
            return keithley_2611()
        elif smu_type == 'keithley26xxab':
            return keithley_26xxab()
        elif smu_type == 'keithley24xx':
            return keithley_24xx()
        elif smu_type == 'agilent_b2900':
            return agilent_b2900()
        else:
            return SMUSimulation()
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            with open('config/config.json', 'r') as f:
                self.config = json.load(f)
                print("Configuration loaded from config/config.json")
                
                # Recreate SMU instance based on loaded config
                self.SMU = self._create_smu_instance()
                
                return True
        except FileNotFoundError:
            print("config/config.json not found. Using default configuration.")
            return False
        except json.JSONDecodeError:
            print("Error decoding config/config.json. Using default configuration.")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open('config/config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
                print("Configuration saved to config/config.json")
                return True
        except Exception as e:
            print(f"Error saving config/config.json: {e}")
            return False
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update configuration"""
        old_smu_type = self.config['global'].get('smu_type', 'simulation')
        
        self.config['IV'].update(new_config['IV'])
        self.config['RT'].update(new_config['RT'])
        self.config['global'].update(new_config['global'])
        
        # Check if SMU type changed and recreate SMU instance if needed
        new_smu_type = self.config['global'].get('smu_type', 'simulation')
        if old_smu_type != new_smu_type:
            self.SMU = self._create_smu_instance()
            print(f"SMU type changed from {old_smu_type} to {new_smu_type}")
        
        self.save_config()
    
    # State machine methods
    def switch(self, currentState: int) -> None:
        """State machine switch function"""
        return self.switcher.get(currentState, self.default)()
    
    def state_machine_function(self) -> None:
        """Execute current state"""
        print(f"go to state_machine_function, current state: {self.currState}")
        self.switch(self.currState)
    
    def initializer(self) -> None:
        """Initialize state"""
        self.currState = self.state['wait_for_event']
    
    def waiter(self) -> None:
        """Wait state - do nothing, just return"""
        print("go to main_window waiter")
    
    def starter(self) -> None:
        """Start measurement process"""
        self.started = True
        self.data.index = 0
        print('Started measurement')
        
        # Only clear data if measurement mode changed
        if self.last_meas_mode != self.config['global']['meas_mode']:
            self.data.clear_all_data()
        
        # Store current measurement mode
        self.last_meas_mode = self.config['global']['meas_mode']
        
        if not self._setup_smu_connection():
            return
        
        self._configure_smu_basic()
        
        # The specific starters (iv_starter, rt_starter) are called by the presenter
        # after setting up the timer
    
    def stoper(self) -> None:
        """Stop measurement process"""
        print('stop')
        
        # Close file
        if self.data.file_handle and not self.data.file_handle.closed:
            self.data.file_handle.close()
        
        # Reset SMU
        self.SMU.reset_smu()
        self.SMU.set_output_off()
        self.SMU.close_smu()
        self.started = False
        self.data.repeat += 1
        
        # Save current data
        self.data.save_current_data()
        
        # Return to wait state
        self.currState = self.state['wait_for_event']
    
    def exiter(self) -> None:
        """Exit application"""
        print('exit')
        if self.started:
            self.currState = self.state['stop']
        # Don't call state_machine_function() here - let the presenter handle the exit
    
    def saver(self) -> None:
        """Save data state"""
        if self.data.file_handle and not self.data.file_handle.closed:
            self.data.file_handle.close()
        
        self.currState = self.state['stop']
    
    def default(self) -> None:
        """Default state handler"""
        print("Unknown state")
    
    # SMU connection methods
    def _setup_smu_connection(self) -> bool:
        """Setup SMU connection with comprehensive error handling"""
        visa_name = self.config['global']['visa_name']
        smu_type = self.config['global'].get('smu_type', 'simulation')
        
        # For simulation SMU, always succeed
        if smu_type == 'simulation':
            try:
                self.SMU.create_smu_connector(visa_name)
                print(f"[{smu_type.upper()}] Connected (simulated)")
                return True
            except Exception as e:
                print(f"Error connecting to simulation SMU: {e}")
                return False
        
        # For real SMUs, check if VISA name is provided
        if not visa_name or visa_name.strip() == '':
            print(f"❌ ERROR: No VISA address provided for {smu_type}")
            print("   Please configure a valid VISA address in the Configuration Dialog")
            self.currState = self.state['wait_for_event']
            return False
        
        try:
            # Attempt to connect to the device
            print(f"🔌 Attempting to connect to {smu_type} at {visa_name}...")
            self.SMU.create_smu_connector(visa_name)
            
            # Try to identify the device
            try:
                device_id = self.SMU.identify_smu()
                print(f"✅ Connected to {smu_type}")
                print(f"   Device ID: {device_id.strip()}")
                return True
            except Exception as e:
                print(f"⚠️  Connected to {visa_name} but device identification failed: {e}")
                print("   Device may not be responding properly")
                return False
                
        except pyvisa.VisaIOError as e:
            error_msg = str(e)
            if "VI_ERROR_RSRC_NFOUND" in error_msg:
                print(f"❌ ERROR: Device not found at {visa_name}")
                print("   Possible causes:")
                print("   - Device is not powered on")
                print("   - Device is not connected")
                print("   - VISA address is incorrect")
                print("   - GPIB/USB driver not installed")
            elif "VI_ERROR_RSRC_BUSY" in error_msg:
                print(f"❌ ERROR: Device at {visa_name} is busy")
                print("   Another application may be using the device")
            elif "VI_ERROR_TMO" in error_msg:
                print(f"❌ ERROR: Connection timeout to {visa_name}")
                print("   Device may be slow to respond or not ready")
            else:
                print(f"❌ ERROR: Connection failed to {visa_name}")
                print(f"   Error: {error_msg}")
            
            self.currState = self.state['wait_for_event']
            return False
            
        except Exception as e:
            print(f"❌ ERROR: Unexpected error connecting to {visa_name}")
            print(f"   Error: {e}")
            self.currState = self.state['wait_for_event']
            return False
    
    def _configure_smu_basic(self) -> None:
        """Configure basic SMU settings with error handling"""
        try:
            self.SMU.reset_smu()
            print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Reset")
        except Exception as e:
            print(f"⚠️  Warning: SMU reset failed: {e}")
        
        try:
            self.SMU.timeout_smu(25000)
            print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Timeout set to 25000s")
        except Exception as e:
            print(f"⚠️  Warning: Timeout setting failed: {e}")
        
        # Set terminal
        try:
            if self.config['global']['terminal'] == 'FRON':
                self.SMU.set_front_terminal()
                print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Using front terminal")
            elif self.config['global']['terminal'] == 'REAR':
                self.SMU.set_rear_terminal()
                print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Using rear terminal")
        except Exception as e:
            print(f"⚠️  Warning: Terminal setting failed: {e}")
    
    def _configure_voltage_source(self, voltage_range: float, voltage_level: float) -> None:
        """Configure voltage source settings with error handling"""
        try:
            self.SMU.set_source_function_voltage()
            print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Source function set to voltage")
        except Exception as e:
            print(f"❌ ERROR: Failed to set source function to voltage: {e}")
            raise
        
        try:
            if voltage_range == 0:
                self.SMU.set_voltage_range_auto_on()
                print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Voltage range set to auto")
            else:
                self.SMU.set_voltage_range_value(voltage_range)
                print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Voltage range set to {voltage_range} V")
        except Exception as e:
            print(f"❌ ERROR: Failed to set voltage range: {e}")
            raise
        
        try:
            self.SMU.set_voltage_level(voltage_level)
            print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Voltage level set to {voltage_level} V")
        except Exception as e:
            print(f"❌ ERROR: Failed to set voltage level: {e}")
            raise
    
    def _configure_current_measurement(self, current_range: float) -> None:
        """Configure current measurement settings with error handling"""
        try:
            self.SMU.set_measure_mode_current()
            print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Measure mode: current")
        except Exception as e:
            print(f"❌ ERROR: Failed to set measure mode to current: {e}")
            raise
        
        try:
            self.SMU.set_measure_current_range(current_range)
            print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Current range: {current_range} A")
        except Exception as e:
            print(f"❌ ERROR: Failed to set current range: {e}")
            raise
        
        try:
            self.SMU.set_measure_current_limit(current_range)
            print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] Current limit: {current_range} A")
        except Exception as e:
            print(f"❌ ERROR: Failed to set current limit: {e}")
            raise
        
        try:
            self.SMU.set_measure_current_nplc(self.config['global']['nplc'])
            print(f"[{self.config['global'].get('smu_type', 'simulation').upper()}] NPLC set to {self.config['global']['nplc']}")
        except Exception as e:
            print(f"❌ ERROR: Failed to set NPLC: {e}")
            raise
    
    def _create_data_file(self, mode_prefix: str) -> bool:
        """Create data file for measurements"""
        currentTime = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        file_name = f'{mode_prefix}{self.config["global"]["file_name"]}{currentTime}.txt'
        self.data.filepath = os.path.join(self.config['global']['save_folder'], file_name)
        
        try:
            self.data.file_handle = open(self.data.filepath, "w")
            return True
        except OSError:
            print('Cannot open/create file in the location')
            self.started = False
            return False
    
    def goto_voltage(self, set_voltage: float, num_step: int) -> None:
        """Gradually increase voltage to target value"""
        delta_voltage = set_voltage / num_step
        for i in range(num_step + 1):
            output_voltage = i * delta_voltage
            self.SMU.set_voltage_level(output_voltage)
            time.sleep(0.01)
            self.SMU.readout()
    
    # IV measurement methods
    def iv_starter(self) -> None:
        """Start IV measurement"""
        print('Starting IV measurement')
        
        self.data.numberStep = round((self.config['IV']['stopV'] - self.config['IV']['startV']) / self.config['IV']['stepV'])
        if self.data.numberStep < 1:
            print('Please check parameters')
            return
        
        # Create voltage list
        self.data.x_vals.clear()
        self.data.y_vals.clear()
        self.data.listV.clear()
        for i in range(self.data.numberStep + 1):
            value = self.config['IV']['startV'] + i * self.config['IV']['stepV']
            self.data.listV.append(value)
        
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
        self.data.file_handle.write('voltage\tcurrent\n')
        
        # Calculate timeout for IV measurement
        timeout = int(round(self.config['global']['nplc'] * 16.67) + self.config['IV']['source_delay_ms'] + 50)
        
        # Start measurement
        self.currState = self.state['wait_for_event']
        self.state_machine_function()
        
        return timeout
    
    def iv_get_plot(self) -> Tuple[List[float], List[float]]:
        """Handle IV measurement plotting - returns (x_vals, y_vals)"""
        if self.data.index < len(self.data.listV):
            voltage = self.data.listV[self.data.index]
            current = self.read_current_out(voltage)
            
            self.data.x_vals.append(voltage)
            self.data.y_vals.append(current)
            self.data.logy_curr_data.append(abs(current))
            
            # Write to file
            if self.data.file_handle and not self.data.file_handle.closed:
                self.data.file_handle.write(f'{voltage}\t{current}\n')
                self.data.file_handle.flush()
            
            self.data.index += 1
            
            # Continue measurement if not finished
            if self.data.index >= len(self.data.listV):
                # Measurement complete
                self.currState = self.state['save_data']
        else:
            self.currState = self.state['save_data']
        
        return self.data.x_vals, self.data.y_vals
    
    def read_current_out(self, voltage: float) -> float:
        """Read current output for given voltage with error handling"""
        try:
            self.SMU.set_voltage_level(voltage)
            time.sleep(self.config['IV']['source_delay_ms'] / 1000.0)
            return self.SMU.readout()
        except Exception as e:
            print(f"❌ ERROR: Failed to read current at voltage {voltage}V: {e}")
            # Return a safe default value (0 current) to prevent crashes
            return 0.0
    
    # RT measurement methods
    def rt_starter(self) -> None:
        """Start RT measurement"""
        print('Starting RT measurement')
        
        # Configure SMU for RT measurement
        self._configure_voltage_source(self.config['RT']['rt_voltage_range'], self.config['RT']['rt_voltage_set'])
        self.SMU.set_source_voltage_delay_auto_on()
        self._configure_current_measurement(self.config['RT']['rt_current_range'])
        self.SMU.set_output_on()
        
        # Go to voltage set point
        if self.data.repeat == 0:
            self.goto_voltage(self.config['RT']['rt_voltage_set'], 10)
        else:
            self.SMU.set_voltage_level(self.config['RT']['rt_voltage_set'])
            time.sleep(0.05)
        
        # Create data file
        if not self._create_data_file('RT'):
            return
        
        # Write header and start measurement
        self.data.file_handle.write('time\tcurrent\n')
        
        # Reset current data for new measurement run
        self.data.reset_for_new_measurement()
        
        # Set start time AFTER SMU setup but BEFORE first measurement
        self.data.start_time = time.time()
        
        # Calculate timeout for RT measurement
        timeout = int(round(self.config['RT']['rt_aperture'] * 1000))
        
        self.currState = self.state['wait_for_event']
        self.state_machine_function()
        
        return timeout
    
    def rt_get_plot(self) -> Tuple[List[float], List[float]]:
        """Handle RT measurement plotting - returns (x_vals, y_vals)"""
        print("go to main_window rt_get_plot")
        try:
            current = self.SMU.readout()
            current_time = time.time() - self.data.start_time
            
            self.data.x_vals.append(current_time)
            self.data.y_vals.append(current)
            
            # Write to file
            if self.data.file_handle and not self.data.file_handle.closed:
                self.data.file_handle.write(f'{current_time}\t{current}\n')
                self.data.file_handle.flush()
            
            return self.data.x_vals, self.data.y_vals
        except Exception as e:
            print(f"❌ ERROR: Failed to read current in RT measurement: {e}")
            # Return current data without adding new point to prevent crashes
            return self.data.x_vals, self.data.y_vals
    
    # Public interface methods
    def get_measurement_data(self) -> MeasurementData:
        """Get current measurement data"""
        return self.data
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config
    
    def is_started(self) -> bool:
        """Check if measurement is started"""
        return self.started
    
    def get_current_state(self) -> int:
        """Get current state"""
        return self.currState
    
    def set_state(self, state: int) -> None:
        """Set current state"""
        self.currState = state
        self.state_machine_function()
    
    def clear_data(self) -> None:
        """Clear all measurement data"""
        self.data.clear_all_data()
        self.last_meas_mode = None
    
    def test_smu_connection(self) -> bool:
        """Test SMU connection and return status"""
        smu_type = self.config['global'].get('smu_type', 'simulation')
        visa_name = self.config['global']['visa_name']
        
        print(f"🔍 Testing connection to {smu_type}...")
        
        # For simulation, always return True
        if smu_type == 'simulation':
            print("✅ Simulation SMU - connection test passed")
            return True
        
        # For real SMUs, check if VISA name is provided
        if not visa_name or visa_name.strip() == '':
            print("❌ No VISA address configured")
            return False
        
        try:
            # Create a temporary SMU instance for testing
            test_smu = self._create_smu_instance()
            test_smu.create_smu_connector(visa_name)
            
            # Try to identify the device
            device_id = test_smu.identify_smu()
            print(f"✅ Connection test passed")
            print(f"   Device ID: {device_id.strip()}")
            
            # Clean up
            test_smu.close_smu()
            return True
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def list_available_devices(self) -> List[str]:
        """List all available VISA devices"""
        try:
            rm = pyvisa.ResourceManager()
            resources = rm.list_resources()
            print(f"🔍 Found {len(resources)} VISA resources:")
            for i, resource in enumerate(resources):
                print(f"   {i+1}. {resource}")
            return resources
        except Exception as e:
            print(f"❌ Error listing VISA resources: {e}")
            return [] 