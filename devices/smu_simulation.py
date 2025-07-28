# devices/smu_simulation.py
import random
from devices.smu_base import SMUBase

class SMUSimulation(SMUBase):
    def __init__(self):
        super().__init__()
        self.connected = False
        self.voltage = 0.0
        self.current = 0.0
        self.output_on = False

    def create_smu_connector(self, visa_resource_name):
        self.connected = True
        print("[SIM] Connected (simulated)")

    def reset_smu(self):
        self.voltage = 0.0
        self.output_on = False
        print("[SIM] Reset")

    def identify_smu(self):
        return "Keithley 2450 Simulation"

    def query_smu(self, command):
        return f"[SIM] Query received: {command}"

    def write_smu(self, command):
        print(f"[SIM] Write: {command}")

    def read_smu(self):
        return "[SIM] Read placeholder"

    def timeout_smu(self, time_s):
        print(f"[SIM] Timeout set to {time_s}s")

    def set_front_terminal(self):
        print("[SIM] Using front terminal")

    def set_rear_terminal(self):
        print("[SIM] Using rear terminal")

    def set_source_voltage_delay_auto_on(self):
        print("[SIM] Auto delay ON")

    def set_source_voltage_delay_auto_off(self):
        print("[SIM] Auto delay OFF")

    def set_source_voltage_delay_time(self, time_ms):
        print(f"[SIM] Delay time set to {time_ms} ms")

    def set_source_function_voltage(self):
        print("[SIM] Source function set to voltage")

    def set_source_function_current(self):
        print("[SIM] Source function set to current")

    def set_voltage_range_auto_on(self):
        print("[SIM] Voltage range AUTO ON")

    def set_voltage_range_auto_off(self):
        print("[SIM] Voltage range AUTO OFF")

    def set_voltage_range_value(self, voltage_range):
        print(f"[SIM] Voltage range set to {voltage_range} V")

    def set_voltage_level(self, voltage_level):
        # voltage_level is a string
        self.voltage = voltage_level
        print(f"[SIM] Voltage level set to {voltage_level} V")

    def set_measure_mode_current(self):
        print("[SIM] Measure mode: current")

    def set_measure_current_range(self, current_range):
        print(f"[SIM] Current range: {current_range} A")

    def set_measure_current_limit(self, current_limit):
        print(f"[SIM] Current limit: {current_limit} A")

    def set_measure_current_nplc(self, nplc_value):
        print(f"[SIM] NPLC set to {nplc_value}")

    def set_output_on(self):
        self.output_on = True
        print("[SIM] Output ON")

    def set_output_off(self):
        self.output_on = False
        print("[SIM] Output OFF")

    def readout(self):
        if self.output_on:
            # Simulate I = V / R + noise, R = 1k
            current = (self.voltage / 1000.0) + random.uniform(-1e-6, 1e-6)
            self.current = current
            return current
        else:
            return 0.0

    def close_smu(self):
        self.connected = False
        print("[SIM] Closed")
