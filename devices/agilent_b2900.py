import pyvisa

class agilent_b2900:
    def __init__(self):
        self.visaResourceName = None
        self.rm = pyvisa.ResourceManager()
        self.Agilent = None

    # establish a connection for the SMU
    def create_smu_connector(self, visaResourceName):
        self.visaResourceName = visaResourceName
        self.Agilent = self.rm.open_resource(self.visaResourceName)
        
    def reset_smu(self):
        self.Agilent.write('*RST')
        
    def identify_smu(self):
        return self.Agilent.query('*IDN?')
        
    def query_smu(self, command):
        return self.Agilent.query(command)
        
    def write_smu(self, command):
        self.Agilent.write(command)
        
    def read_smu(self):
        return self.Agilent.read()

    # standard time out is 25 seconds
    def timeout_smu(self, time_s):
        self.Agilent.timeout = time_s

    '''set the terminal output front or rear'''
    def set_front_terminal(self):
        # Agilent B2900 typically uses front terminals by default
        # This command may not be needed for B2900
        pass
        
    def set_rear_terminal(self):
        # Agilent B2900 typically uses front terminals by default
        # This command may not be needed for B2900
        pass
        
    '''set the source functions'''

    '''set the source voltage delay auto on'''
    def set_source_voltage_delay_auto_on(self):
        # Agilent B2900 uses different delay commands
        self.Agilent.write(":SOUR:VOLT:DEL:AUTO ON")
        
    def set_source_voltage_delay_auto_off(self):
        self.Agilent.write(":SOUR:VOLT:DEL:AUTO OFF")
        
    def set_source_voltage_delay_time(self, time_ms):
        source_delay = float(time_ms) / 1000
        self.Agilent.write(f":SOUR:VOLT:DEL {source_delay}")

    '''set source function as voltage output'''
    def set_source_function_voltage(self):
        self.Agilent.write(':SOUR:FUNC VOLT')
        
    def set_source_function_current(self):
        self.Agilent.write(':SOUR:FUNC CURR')

    '''set voltage range auto or value'''
    def set_voltage_range_auto_on(self):
        self.Agilent.write(":SOUR:VOLT:RANG:AUTO ON")
        
    def set_voltage_range_auto_off(self):
        self.Agilent.write(":SOUR:VOLT:RANG:AUTO OFF")
        
    def set_voltage_range_value(self, voltage_range):
        self.Agilent.write(f":SOUR:VOLT:RANG {voltage_range}")

    def set_voltage_level(self, voltage_level):
        self.Agilent.write(f":SOUR:VOLT:LEV {voltage_level}")
        
    '''measurement mode and range'''
    def set_measure_mode_current(self):
        self.Agilent.write(":SENS:FUNC 'CURR'")
        
    # for example current:range = 1e-3 , 1 mA
    def set_measure_current_range(self, current_range):
        self.Agilent.write(f":SENS:CURR:RANG {current_range}")
        
    def set_measure_current_limit(self, current_limit):
        self.Agilent.write(f":SOUR:VOLT:ILIM {current_limit}")
        
    '''set nplc value for current measurement'''
    def set_measure_current_nplc(self, nplc_value):
        self.Agilent.write(f"SENS:CURR:NPLC {nplc_value}")
        
    '''smu output on/ off'''
    def set_output_on(self):
        self.Agilent.write('OUTP ON')
        
    def set_output_off(self):
        self.Agilent.write('OUTP OFF')
        
    '''readout from agilent'''
    def readout(self):
        self.Agilent.write(":READ?")
        return float(self.Agilent.read())
        
    def close_smu(self):
        self.Agilent.close()


# Test code for Agilent B2900
if __name__ == '__main__':
    current_smu = agilent_b2900()
    current_smu.create_smu_connector('GPIB0::18::INSTR')

    current_smu.timeout_smu(25)

    current_smu.set_front_terminal()
    current_smu.set_source_function_voltage()
    current_smu.set_measure_mode_current()
    current_smu.set_measure_current_range(100e-3)
    current_smu.set_measure_current_limit(50e-3)
    current_smu.set_voltage_range_auto_on()

    current_smu.set_voltage_level(2.1)
    current_smu.set_measure_current_nplc(0.1)
    current_smu.set_output_on()

    print(current_smu.query_smu(':SENS:CURR:NPLC?'))
    current_smu.set_output_off()
    current_smu.close_smu() 