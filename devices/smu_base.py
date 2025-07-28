# devices/smu_base.py
from abc import ABC, abstractmethod

class SMUBase(ABC):
    def __init__(self):
        self.visa_resource_name = None

    @abstractmethod
    def create_smu_connector(self, visa_resource_name):
        pass

    @abstractmethod
    def reset_smu(self):
        pass

    @abstractmethod
    def identify_smu(self):
        pass

    @abstractmethod
    def query_smu(self, command):
        pass

    @abstractmethod
    def write_smu(self, command):
        pass

    @abstractmethod
    def read_smu(self):
        pass

    @abstractmethod
    def timeout_smu(self, time_s):
        pass

    @abstractmethod
    def set_front_terminal(self):
        pass

    @abstractmethod
    def set_rear_terminal(self):
        pass

    @abstractmethod
    def set_source_voltage_delay_auto_on(self):
        pass

    @abstractmethod
    def set_source_voltage_delay_auto_off(self):
        pass

    @abstractmethod
    def set_source_voltage_delay_time(self, time_ms):
        pass

    @abstractmethod
    def set_source_function_voltage(self):
        pass

    @abstractmethod
    def set_source_function_current(self):
        pass

    @abstractmethod
    def set_voltage_range_auto_on(self):
        pass

    @abstractmethod
    def set_voltage_range_auto_off(self):
        pass

    @abstractmethod
    def set_voltage_range_value(self, voltage_range):
        pass

    @abstractmethod
    def set_voltage_level(self, voltage_level):
        pass

    @abstractmethod
    def set_measure_mode_current(self):
        pass

    @abstractmethod
    def set_measure_current_range(self, current_range):
        pass

    @abstractmethod
    def set_measure_current_limit(self, current_limit):
        pass

    @abstractmethod
    def set_measure_current_nplc(self, nplc_value):
        pass

    @abstractmethod
    def set_output_on(self):
        pass

    @abstractmethod
    def set_output_off(self):
        pass

    @abstractmethod
    def readout(self):
        pass

    @abstractmethod
    def close_smu(self):
        pass
