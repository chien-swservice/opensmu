import pyvisa

class keithley_2450:
    def __init__(self):
        self.visaResourceName = None
        self.rm = pyvisa.ResourceManager()
        self.Keithley = None

    # establish a connection for the SMU as to try this one for error handling
    # generate GpibInstrument
    def create_smu_connector(self, visaResourceName):
        self.visaResourceName = visaResourceName
        self.Keithley = self.rm.open_resource(self.visaResourceName)
    '''tested'''
    def reset_smu(self):
        self.Keithley.write('*RST')
    '''tested'''
    def identify_smu(self):
        return self.Keithley.query('*IDN?')
    '''tested'''
    def query_smu(self, command):
        return self.Keithley.query(command)
    '''tested'''
    def write_smu(self, command):
        self.Keithley.write(command)
    '''tested'''
    def read_smu(self):
        return self.Keithley.read()

    # standard time out is 25 seconds
    def timeout_smu(self, time_s):
        self.Keithley.timeout = time_s

    '''set the terminal output front or rear'''
    '''tested'''
    def set_front_terminal(self):
        self.Keithley.write(':ROUT:TERM FRON')
    '''tested'''
    def set_rear_terminal(self):
        self.Keithley.write(':ROUT:TERM REAR')
    '''set the source functions'''

    '''set the source voltage delay auto on'''
    # test source voltage delay
    # current_smu.set_source_voltage_delay_time(500)
    # print(current_smu.query_smu(':SOUR:VOLT:DEL?'))
    '''tested'''
    def set_source_voltage_delay_auto_on(self):
        self.Keithley.write(":SOUR:VOLT:DEL:AUTO ON")
    '''tested'''
    def set_source_voltage_delay_auto_off(self):
        self.Keithley.write(":SOUR:VOLT:DEL:AUTO OFF")
    '''tested'''
    def set_source_voltage_delay_time(self, time_ms):
        source_delay = float(time_ms) / 1000
        self.Keithley.write(f":SOUR:VOLT:DEL {source_delay}")

    '''set source function as voltage output'''
    '''tested'''
    # current_smu.set_source_function_voltage()
    # print(current_smu.query_smu(':SOUR:FUNC?'))
    def set_source_function_voltage(self):
        self.Keithley.write(':SOUR:FUNC VOLT')
    '''tested'''
    def set_source_function_current(self):
        self.Keithley.write(':SOUR:FUNC CURR')

    '''set voltage range auto or value'''
    # current_smu.set_voltage_range_value(10)
    # print(current_smu.query_smu(':SOUR:VOLT:RANG?'))
    '''tested'''
    def set_voltage_range_auto_on(self):
        self.Keithley.write(":SOUR:VOLT:RANG:AUTO ON")
    '''tested'''
    def set_voltage_range_auto_off(self):
        self.Keithley.write(":SOUR:VOLT:RANG:AUTO OFF")
    '''tested'''
    def set_voltage_range_value(self, voltage_range):
        self.Keithley.write(f":SOUR:VOLT:RANG {voltage_range}")

    '''tested'''
    # voltage_level: float?
    def set_voltage_level(self, voltage_level):
        self.Keithley.write(f":SOUR:VOLT:LEV {voltage_level}")
    '''tested'''
    '''measurement mode and range'''
    def set_measure_mode_current(self):
        self.Keithley.write(":SENS:FUNC 'CURR'")
    '''tested'''
    # for example current:range = 1e-3 , 1 mA
    def set_measure_current_range(self, current_range):
        self.Keithley.write(f":SENS:CURR:RANG {current_range}")
    '''tested'''
    # current_limit: float?
    def set_measure_current_limit(self, current_limit):
        self.Keithley.write(f":SOUR:VOLT:ILIM {current_limit}")
    '''tested'''
    '''set nplc value for current measurement'''
    def set_measure_current_nplc(self, nplc_value):
        self.Keithley.write(f"SENS:CURR:NPLC {nplc_value}")
    '''tested'''
    '''smu output on/ off'''
    def set_output_on(self):
        self.Keithley.write('OUTP ON')
    '''tested'''
    def set_output_off(self):
        self.Keithley.write('OUTP OFF')
    '''tested'''
    '''readout from keithley'''
    def readout(self):
        self.Keithley.write(":READ?")
        return float(self.Keithley.read())
    '''do not know how to test'''
    def close_smu(self):
        self.Keithley.close()
        # self.Keithley.close

    '''command to implement'''
    # *CLS
    # *ESE
    # *ESE?
    # *ESR?
    # *IDN?


# if __name__ == '__main__':
#     current_smu = keithley_2450('GPIB0::18::INSTR')
#     current_smu.create_smu_connector()
#
#     current_smu.timeout_smu(25)
#
#     current_smu.set_front_terminal()
#     current_smu.set_source_function_voltage()
#     current_smu.set_measure_mode_current()
#     current_smu.set_measure_current_range(100e-3)
#     current_smu.set_measure_current_limit(50e-3)
#     current_smu.set_voltage_range_auto_on()
#
#     current_smu.set_voltage_level(2.1)
#     current_smu.set_measure_current_nplc(0.1)
#     current_smu.set_output_on()
#
#     # print(current_smu.readout())
#
#     print(current_smu.query_smu(':SENS:CURR:NPLC?'))
#     # print(current_smu.read_smu())
#     current_smu.set_output_off()
#     current_smu.close_smu()
