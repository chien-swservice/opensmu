import pyvisa

class keithley_26xxab:
    def __init__(self):
        self.visaResourceName = None
        self.rm = pyvisa.ResourceManager()
        self.Keithley = None

    # establish a connection for the SMU
    def create_smu_connector(self, visaResourceName):
        self.visaResourceName = visaResourceName
        self.Keithley = self.rm.open_resource(self.visaResourceName)
        
    def reset_smu(self):
        self.Keithley.write('*RST')
        
    def identify_smu(self):
        return self.Keithley.query('*IDN?')
        
    def query_smu(self, command):
        return self.Keithley.query(command)
        
    def write_smu(self, command):
        self.Keithley.write(command)
        
    def read_smu(self):
        return self.Keithley.read()

    # standard time out is 25 seconds
    def timeout_smu(self, time_s):
        self.Keithley.timeout = time_s

    '''set the terminal output front or rear'''
    def set_front_terminal(self):
        self.Keithley.write(':ROUT:TERM FRON')
        
    def set_rear_terminal(self):
        self.Keithley.write(':ROUT:TERM REAR')
        
    '''set the source functions'''

    '''set the source voltage delay auto on'''
    def set_source_voltage_delay_auto_on(self):
        self.Keithley.write(":SOUR:VOLT:DEL:AUTO ON")
        
    def set_source_voltage_delay_auto_off(self):
        self.Keithley.write(":SOUR:VOLT:DEL:AUTO OFF")
        
    def set_source_voltage_delay_time(self, time_ms):
        source_delay = float(time_ms) / 1000
        self.Keithley.write(f":SOUR:VOLT:DEL {source_delay}")

    '''set source function as voltage output'''
    def set_source_function_voltage(self):
        self.Keithley.write(':SOUR:FUNC VOLT')
        
    def set_source_function_current(self):
        self.Keithley.write(':SOUR:FUNC CURR')

    '''set voltage range auto or value'''
    def set_voltage_range_auto_on(self):
        self.Keithley.write(":SOUR:VOLT:RANG:AUTO ON")
        
    def set_voltage_range_auto_off(self):
        self.Keithley.write(":SOUR:VOLT:RANG:AUTO OFF")
        
    def set_voltage_range_value(self, voltage_range):
        self.Keithley.write(f":SOUR:VOLT:RANG {voltage_range}")

    def set_voltage_level(self, voltage_level):
        self.Keithley.write(f":SOUR:VOLT:LEV {voltage_level}")
        
    '''measurement mode and range'''
    def set_measure_mode_current(self):
        self.Keithley.write(":SENS:FUNC 'CURR'")
        
    # for example current:range = 1e-3 , 1 mA
    def set_measure_current_range(self, current_range):
        self.Keithley.write(f":SENS:CURR:RANG {current_range}")
        
    def set_measure_current_limit(self, current_limit):
        self.Keithley.write(f":SOUR:VOLT:ILIM {current_limit}")
        
    '''set nplc value for current measurement'''
    def set_measure_current_nplc(self, nplc_value):
        self.Keithley.write(f"SENS:CURR:NPLC {nplc_value}")
        
    '''smu output on/ off'''
    def set_output_on(self):
        self.Keithley.write('OUTP ON')
        
    def set_output_off(self):
        self.Keithley.write('OUTP OFF')
        
    '''readout from keithley'''
    def readout(self):
        self.Keithley.write(":READ?")
        return float(self.Keithley.read())
        
    def close_smu(self):
        self.Keithley.close()


# Test code for Keithley 26xxAB
if __name__ == '__main__':
    current_smu = keithley_26xxab()
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