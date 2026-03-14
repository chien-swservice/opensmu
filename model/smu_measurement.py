"""SMU measurement logic — connection, configuration, IV and RT measurements."""
import time
import os
import datetime
from typing import Tuple, List
import pyvisa

from .smu_state import SMUState


class SMUMeasurementMixin:
    """Mixin providing SMU connection, configuration, and measurement methods."""

    # --- Connection ---

    def _setup_smu_connection(self) -> bool:
        """Connect to the SMU with error handling."""
        visa_name = self.config['global']['visa_name']
        smu_type = self.config['global'].get('smu_type', 'simulation')

        if smu_type == 'simulation':
            try:
                self.SMU.create_smu_connector(visa_name)
                print(f"[{smu_type.upper()}] Connected (simulated)")
                return True
            except Exception as e:
                print(f"Error connecting to simulation SMU: {e}")
                return False

        if not visa_name or visa_name.strip() == '':
            print(f"❌ ERROR: No VISA address provided for {smu_type}")
            print("   Please configure a valid VISA address in the Configuration Dialog")
            self.currState = SMUState.WAIT_FOR_EVENT
            return False

        try:
            print(f"🔌 Attempting to connect to {smu_type} at {visa_name}...")
            self.SMU.create_smu_connector(visa_name)
            try:
                device_id = self.SMU.identify_smu()
                print(f"✅ Connected to {smu_type}")
                print(f"   Device ID: {device_id.strip()}")
                return True
            except Exception as e:
                print(f"⚠️  Connected to {visa_name} but device identification failed: {e}")
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
                print(f"❌ ERROR: Connection failed to {visa_name}: {error_msg}")
            self.currState = SMUState.WAIT_FOR_EVENT
            return False

        except Exception as e:
            print(f"❌ ERROR: Unexpected error connecting to {visa_name}: {e}")
            self.currState = SMUState.WAIT_FOR_EVENT
            return False

    def test_smu_connection(self) -> bool:
        """Test SMU connection without starting a measurement."""
        smu_type = self.config['global'].get('smu_type', 'simulation')
        visa_name = self.config['global']['visa_name']

        print(f"🔍 Testing connection to {smu_type}...")

        if smu_type == 'simulation':
            print("✅ Simulation SMU - connection test passed")
            return True

        if not visa_name or visa_name.strip() == '':
            print("❌ No VISA address configured")
            return False

        try:
            test_smu = self._create_smu_instance()
            test_smu.create_smu_connector(visa_name)
            device_id = test_smu.identify_smu()
            print(f"✅ Connection test passed")
            print(f"   Device ID: {device_id.strip()}")
            test_smu.close_smu()
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

    # --- Private helpers ---

    def _smu_warn(self, fn, success_msg: str, warning_msg: str, *args) -> None:
        """Call an SMU command, print a warning on failure but continue."""
        try:
            fn(*args)
            print(success_msg)
        except Exception as e:
            print(f"⚠️  Warning: {warning_msg}: {e}")

    def _smu_cmd(self, fn, success_msg: str, error_msg: str, *args) -> None:
        """Call an SMU command, print an error and re-raise on failure."""
        try:
            fn(*args)
            print(success_msg)
        except Exception as e:
            print(f"❌ ERROR: {error_msg}: {e}")
            raise

    # --- SMU configuration ---

    def _configure_smu_basic(self) -> None:
        """Reset SMU, set timeout and terminal."""
        lbl = self.config['global'].get('smu_type', 'simulation').upper()

        self._smu_warn(self.SMU.reset_smu,
                       f"[{lbl}] Reset", "SMU reset failed")
        self._smu_warn(self.SMU.timeout_smu,
                       f"[{lbl}] Timeout set to 25000s", "Timeout setting failed",
                       25000)

        try:
            if self.config['global']['terminal'] == 'FRONT':
                self.SMU.set_front_terminal()
                print(f"[{lbl}] Using front terminal")
            elif self.config['global']['terminal'] == 'REAR':
                self.SMU.set_rear_terminal()
                print(f"[{lbl}] Using rear terminal")
        except Exception as e:
            print(f"⚠️  Warning: Terminal setting failed: {e}")

    def _configure_voltage_source(self, voltage_range: float, voltage_level: float) -> None:
        """Set source function, voltage range and initial voltage level."""
        lbl = self.config['global'].get('smu_type', 'simulation').upper()

        self._smu_cmd(self.SMU.set_source_function_voltage,
                      f"[{lbl}] Source function set to voltage",
                      "Failed to set source function to voltage")

        if voltage_range == 0:
            self._smu_cmd(self.SMU.set_voltage_range_auto_on,
                          f"[{lbl}] Voltage range: auto",
                          "Failed to set voltage range to auto")
        else:
            self._smu_cmd(self.SMU.set_voltage_range_value,
                          f"[{lbl}] Voltage range: {voltage_range} V",
                          "Failed to set voltage range",
                          voltage_range)

        self._smu_cmd(self.SMU.set_voltage_level,
                      f"[{lbl}] Voltage level: {voltage_level} V",
                      "Failed to set voltage level",
                      voltage_level)

    def _configure_current_measurement(self, current_range: float) -> None:
        """Set measure mode, current range, limit and NPLC."""
        lbl = self.config['global'].get('smu_type', 'simulation').upper()
        nplc = self.config['global']['nplc']

        self._smu_cmd(self.SMU.set_measure_mode_current,
                      f"[{lbl}] Measure mode: current",
                      "Failed to set measure mode to current")
        self._smu_cmd(self.SMU.set_measure_current_range,
                      f"[{lbl}] Current range: {current_range} A",
                      "Failed to set current range",
                      current_range)
        self._smu_cmd(self.SMU.set_measure_current_limit,
                      f"[{lbl}] Current limit: {current_range} A",
                      "Failed to set current limit",
                      current_range)
        self._smu_cmd(self.SMU.set_measure_current_nplc,
                      f"[{lbl}] NPLC: {nplc}",
                      "Failed to set NPLC",
                      nplc)

    # --- File ---

    def _create_data_file(self, mode_prefix: str) -> bool:
        """Create the output data file, auto-creating the folder if needed."""
        timestamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        file_name = f'{mode_prefix}{self.config["global"]["file_name"]}{timestamp}.txt'
        self.data.filepath = os.path.join(self.config['global']['save_folder'], file_name)

        try:
            os.makedirs(self.config['global']['save_folder'], exist_ok=True)
            self.data.file_handle = open(self.data.filepath, "w")
            return True
        except OSError as e:
            print(f'Cannot open/create file: {e}')
            self.started = False
            return False

    # --- Voltage ramp ---

    def goto_voltage(self, set_voltage: float, num_step: int) -> None:
        """Ramp voltage gradually to target value."""
        delta_voltage = set_voltage / num_step
        for i in range(num_step + 1):
            self.SMU.set_voltage_level(i * delta_voltage)
            time.sleep(0.01)
            self.SMU.readout()

    # --- IV measurement ---

    def iv_starter(self):
        """Configure SMU and prepare data structures for an IV sweep."""
        print('Starting IV measurement')

        self.data.numberStep = round(
            (self.config['IV']['stopV'] - self.config['IV']['startV'])
            / self.config['IV']['stepV']
        )
        if self.data.numberStep < 1:
            print('Please check IV parameters')
            return

        self.data.x_vals.clear()
        self.data.y_vals.clear()
        self.data.listV.clear()
        for i in range(self.data.numberStep + 1):
            self.data.listV.append(self.config['IV']['startV'] + i * self.config['IV']['stepV'])

        self._configure_voltage_source(self.config['IV']['voltage_range'], 0.0)
        self.SMU.set_source_voltage_delay_auto_off()
        self.SMU.set_source_voltage_delay_time(self.config['IV']['source_delay_ms'])
        self._configure_current_measurement(self.config['IV']['current_range'])
        self.SMU.set_output_on()

        self.goto_voltage(self.config['IV']['startV'], 10)

        if not self._create_data_file('IV'):
            return

        self.data.file_handle.write('voltage\tcurrent\n')

        timeout = int(
            round(self.config['global']['nplc'] * 16.67)
            + self.config['IV']['source_delay_ms']
            + 50
        )

        self.currState = SMUState.WAIT_FOR_EVENT
        self.state_machine_function()

        return timeout

    def iv_collect_data(self) -> Tuple[List[float], List[float]]:
        """Collect one IV data point per timer tick."""
        if self.data.index < len(self.data.listV):
            voltage = self.data.listV[self.data.index]
            current = self.read_current_out(voltage)

            self.data.x_vals.append(voltage)
            self.data.y_vals.append(current)
            self.data.logy_curr_data.append(abs(current))

            if self.data.file_handle and not self.data.file_handle.closed:
                self.data.file_handle.write(f'{voltage}\t{current}\n')
                self.data.file_handle.flush()

            self.data.index += 1

            if self.data.index >= len(self.data.listV):
                self.currState = SMUState.SAVE_DATA
        else:
            self.currState = SMUState.SAVE_DATA

        return self.data.x_vals, self.data.y_vals

    def read_current_out(self, voltage: float) -> float:
        """Set voltage and read back current."""
        try:
            self.SMU.set_voltage_level(voltage)
            time.sleep(self.config['IV']['source_delay_ms'] / 1000.0)
            return self.SMU.readout()
        except Exception as e:
            print(f"❌ ERROR: Failed to read current at {voltage} V: {e}")
            return 0.0

    # --- RT measurement ---

    def rt_starter(self):
        """Configure SMU and prepare data structures for real-time monitoring."""
        print('Starting RT measurement')

        self._configure_voltage_source(
            self.config['RT']['rt_voltage_range'],
            self.config['RT']['rt_voltage_set']
        )
        self.SMU.set_source_voltage_delay_auto_on()
        self._configure_current_measurement(self.config['RT']['rt_current_range'])
        self.SMU.set_output_on()

        if self.data.repeat == 0:
            self.goto_voltage(self.config['RT']['rt_voltage_set'], 10)
        else:
            self.SMU.set_voltage_level(self.config['RT']['rt_voltage_set'])
            time.sleep(0.05)

        if not self._create_data_file('RT'):
            return

        self.data.file_handle.write('time\tcurrent\n')
        self.data.reset_for_new_measurement()
        self.data.start_time = time.time()

        timeout = int(round(self.config['RT']['rt_aperture'] * 1000))

        self.currState = SMUState.WAIT_FOR_EVENT
        self.state_machine_function()

        return timeout

    def rt_collect_data(self) -> Tuple[List[float], List[float]]:
        """Collect one RT data point per timer tick."""
        try:
            current = self.SMU.readout()
            current_time = time.time() - self.data.start_time

            self.data.x_vals.append(current_time)
            self.data.y_vals.append(current)

            if self.data.file_handle and not self.data.file_handle.closed:
                self.data.file_handle.write(f'{current_time}\t{current}\n')
                self.data.file_handle.flush()

            return self.data.x_vals, self.data.y_vals
        except Exception as e:
            print(f"❌ ERROR: Failed to read current in RT measurement: {e}")
            return self.data.x_vals, self.data.y_vals
