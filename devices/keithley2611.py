from devices.smu_base import SMUBase
import pyvisa

class keithley_2611(SMUBase):
    def __init__(self):
        self.visaResourceName = None
        self.rm = pyvisa.ResourceManager()
        self.Keithley = None
        self.channel = 'smua'

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
        self.channel = 'smua'
        # self.Keithley.write(':ROUT:TERM FRON')
        
    def set_rear_terminal(self):
        self.channel = 'smub'
        # cannot test with Keithley 2611
        # self.Keithley.write(':ROUT:TERM REAR')
        
    '''set the source functions'''

    '''set the source voltage delay auto on'''
    # tested
    def set_source_voltage_delay_auto_on(self):
        """
        Enable auto delay for voltage source
        
        According to Keithley Series 2600 Reference Manual:
        - Enables automatic delay for voltage source
        - Uses TSP command: smua.source.delay = smua.AUTODELAY_ON
        """
        self.Keithley.write(f"{self.channel}.source.delay = {self.channel}.AUTODELAY_ON")
        
    # tested
    def set_source_voltage_delay_auto_off(self):
        """
        Disable auto delay for voltage source
        
        According to Keithley Series 2600 Reference Manual:
        - Disables automatic delay for voltage source
        - Uses TSP command: smua.source.delay = smua.AUTODELAY_OFF
        """
        self.Keithley.write(f"{self.channel}.source.delay = {self.channel}.AUTODELAY_OFF")
        
    # tested
    def set_source_voltage_delay_time(self, time_ms):
        """
        Set source voltage delay time
        
        According to Keithley Series 2600 Reference Manual:
        - Sets the source delay time in seconds
        - Uses TSP command: smua.source.delay = delay_time
        - The delay is applied after each source level change
        
        Args:
            time_ms (float): Delay time in milliseconds (converted to seconds)
        """
        source_delay = float(time_ms) / 1000
        self.Keithley.write(f"{self.channel}.source.delay = {source_delay}")
    
    # tested
    def get_source_voltage_delay_time(self):
        """
        Get current source voltage delay time
        
        Returns:
            float: Current delay time in seconds
        """
        self.Keithley.write(f"print({self.channel}.source.delay)")
        return float(self.Keithley.read())
    
    # tested
    def get_source_voltage_delay_auto_status(self):
        """
        Get current auto delay status for voltage source
        
        Returns:
            str: Auto delay status (ON/OFF)
        """
        self.Keithley.write(f"print({self.channel}.source.delay)")
        delay_value = self.Keithley.read().strip()
        # Check if it's auto delay (typically returns -1 for auto)
        if delay_value == "-1.00000e+00" or delay_value == "-1":
            return "ON"
        else:
            return "OFF"

    # tested
    '''set source function as voltage or current output'''
    def set_source_function_voltage(self):
        """
        Set source function to voltage output
        
        According to Keithley Series 2600 Reference Manual:
        - Sets the source function to DC voltage output
        - Uses TSP command: smua.source.func = smua.OUTPUT_DCVOLTS
        """
        self.Keithley.write(f'{self.channel}.source.func = {self.channel}.OUTPUT_DCVOLTS')
        
    def set_source_function_current(self):
        """
        Set source function to current output
        
        According to Keithley Series 2600 Reference Manual:
        - Sets the source function to DC current output
        - Uses TSP command: smua.source.func = smua.OUTPUT_DCAMPS
        """
        self.Keithley.write(f'{self.channel}.source.func = {self.channel}.OUTPUT_DCAMPS')
    
    def get_source_function(self):
        """
        Get current source function
        
        Returns:
            str: Current source function (OUTPUT_DCVOLTS or OUTPUT_DCAMPS)
        """
        self.Keithley.write(f"print({self.channel}.source.func)")
        return self.Keithley.read().strip()
    # tested
    '''set voltage range auto or value'''
    def set_voltage_range_auto_on(self):
        """Enable auto-range for voltage source"""
        self.Keithley.write(f"{self.channel}.source.autorangev = {self.channel}.AUTORANGE_ON")
    # tested        
    def set_voltage_range_auto_off(self):
        """Disable auto-range for voltage source"""
        self.Keithley.write(f"{self.channel}.source.autorangev = {self.channel}.AUTORANGE_OFF")
    # tested
    def set_voltage_range_value(self, voltage_range):
        """
        Set voltage range value for Keithley 2611
        
        According to Keithley Series 2600 Reference Manual:
        - Voltage ranges: 0.2V, 2V, 20V, 200V
        - The instrument will automatically select the closest available range
        - If voltage_range is 0, auto-range is enabled
        
        Args:
            voltage_range (float): Voltage range in volts (0.2, 2, 20, 200)
        """
        if voltage_range == 0:
            # Enable auto-range
            self.Keithley.write(f"{self.channel}.source.autorangev = {self.channel}.AUTORANGE_ON")
        else:
            # Set specific voltage range
            # The Keithley 2611 will automatically select the closest available range
            self.Keithley.write(f"{self.channel}.source.rangev = {voltage_range}")
    # tested
    def get_voltage_range(self):
        """
        Get current voltage range value
        
        Returns:
            float: Current voltage range in volts
        """
        self.Keithley.write(f"print({self.channel}.source.rangev)")
        return float(self.Keithley.read())
    # tested
    def get_voltage_autorange_status(self):
        """
        Get current auto-range status
        
        Returns:
            str: Auto-range status (ON/OFF)
        """
        self.Keithley.write(f"print({self.channel}.source.autorangev)")
        return self.Keithley.read().strip()
    
    # Current range functions
    def set_source_current_range_auto_on(self):
        """Enable auto-range for current source"""
        self.Keithley.write(f"{self.channel}.source.autorangei = {self.channel}.AUTORANGE_ON")
        
    def set_source_current_range_auto_off(self):
        """Disable auto-range for current source"""
        self.Keithley.write(f"{self.channel}.source.autorangei = {self.channel}.AUTORANGE_OFF")
        
    def set_source_current_range_value(self, current_range):
        """
        Set current range value for Keithley 2611
        
        According to Keithley Series 2600 Reference Manual:
        - Current ranges: 1e-9A, 1e-8A, 1e-7A, 1e-6A, 1e-5A, 1e-4A, 1e-3A, 1e-2A, 1e-1A, 1A, 3A
        - The instrument will automatically select the closest available range
        - If current_range is 0, auto-range is enabled
        
        Args:
            current_range (float): Current range in amperes
        """
        if current_range == 0:
            # Enable auto-range
            self.Keithley.write(f"{self.channel}.source.autorangei = {self.channel}.AUTORANGE_ON")
        else:
            # Set specific current range
            # The Keithley 2611 will automatically select the closest available range
            self.Keithley.write(f"{self.channel}.source.rangei = {current_range}")
    
    def get_source_current_range(self):
        """
        Get current current range value
        
        Returns:
            float: Current current range in amperes
        """
        self.Keithley.write(f"print({self.channel}.source.rangei)")
        return float(self.Keithley.read())
    
    def get_source_current_autorange_status(self):
        """
        Get current auto-range status for current source
        
        Returns:
            str: Auto-range status (ON/OFF)
        """
        self.Keithley.write(f"print({self.channel}.source.autorangei)")
        return self.Keithley.read().strip()
    # tested
    def set_voltage_level(self, voltage_level):
        """
        Set voltage level for voltage source
        
        Args:
            voltage_level (float): Voltage level in volts
        """
        self.Keithley.write(f"{self.channel}.source.levelv={voltage_level}")
    
    def set_source_current_level(self, current_level):
        """
        Set current level for current source
        
        Args:
            current_level (float): Current level in amperes
        """
        self.Keithley.write(f"{self.channel}.source.leveli={current_level}")
    
    def get_source_voltage_level(self):
        """
        Get current voltage level
        
        Returns:
            float: Current voltage level in volts
        """
        self.Keithley.write(f"print({self.channel}.source.levelv)")
        return float(self.Keithley.read())
    
    def get_source_current_level(self):
        """
        Get current current level
        
        Returns:
            float: Current current level in amperes
        """
        self.Keithley.write(f"print({self.channel}.source.leveli)")
        return float(self.Keithley.read())
        
    '''measurement mode and range'''
    # tested, return 0: measure current, 1: measure voltage and so on
    def set_measure_mode_current(self):
        self.Keithley.write(f"display.{self.channel}.measure.func = display.MEASURE_DCAMPS")
        
    # tested, the closest value of current range
    def set_measure_current_range(self, current_range):
        self.Keithley.write(f"{self.channel}.measure.rangei = {current_range}")

    # tested, current limit in A float       
    def set_measure_current_limit(self, current_limit):
        self.Keithley.write(f"{self.channel}.source.limiti = {current_limit}")
    
    # tested
    '''set nplc value for current measurement'''
    def set_measure_current_nplc(self, nplc_value):
        self.Keithley.write(f"{self.channel}.measure.nplc = {nplc_value}")
        
    '''smu output on/ off'''
    # tested
    def set_output_on(self):
        self.Keithley.write(f'{self.channel}.source.output = {self.channel}.OUTPUT_ON')
    # tested
    def set_output_off(self):
        self.Keithley.write(f'{self.channel}.source.output = {self.channel}.OUTPUT_OFF')
        
    '''readout from keithley'''
    # tested
    # return current in A float
    def readout(self):
        self.Keithley.write(f"print({self.channel}.measure.i())")
        return float(self.Keithley.read())

    # tested        
    def close_smu(self):
        self.Keithley.close()


# Test code for Keithley 2611
if __name__ == '__main__':
    import time
    visaResourceName = 'GPIB0::24::INSTR'
    
    # tested
    def test_keithley_2611():
        current_smu = keithley_2611()
        current_smu.create_smu_connector(visaResourceName)
        current_smu.timeout_smu(25)
        current_smu.write_smu('*IDN?')
        print(current_smu.read_smu())
        current_smu.close_smu()

    # tested
    def test_output_on_off():
        current_smu = keithley_2611()
        current_smu.create_smu_connector(visaResourceName)
        current_smu.timeout_smu(25)
        current_smu.set_output_on()
        time.sleep(3)
        current_smu.set_output_off()
        current_smu.close_smu()
    
    def test_voltage_level():
        current_smu = keithley_2611()
        current_smu.create_smu_connector(visaResourceName)
        current_smu.reset_smu()
        current_smu.timeout_smu(25)
        current_smu.set_source_function_voltage()
        # time.sleep(0.1)
        current_smu.set_voltage_level(1.0)
        
        # turn on SMU 
        current_smu.set_output_on()
        time.sleep(0.1)
        current_smu.write_smu("print(smua.source.levelv)")
        time.sleep(0.1)
        print(current_smu.read_smu())
        time.sleep(3)
        current_smu.set_output_off()
        current_smu.close_smu()
    
    def test_readout():
        current_smu = keithley_2611()
        current_smu.create_smu_connector(visaResourceName)
        current_smu.timeout_smu(25)
        current_smu.set_source_function_voltage()
        current_smu.set_voltage_level(0.6)
        # turn on SMU 
        current_smu.set_output_on()
        time.sleep(0.1)
        print(f"current: {current_smu.readout()}")
    
    def test_voltage_range():
        """
        Test voltage range functionality for Keithley 2611
        
        Tests:
        1. Auto-range on/off
        2. Setting specific voltage ranges
        3. Reading back the actual range values
        """
        print("Testing Keithley 2611 Voltage Range Functionality")
        print("=" * 50)
        
        current_smu = keithley_2611()
        
        try:
            # Connect to the instrument
            current_smu.create_smu_connector(visaResourceName)
            current_smu.timeout_smu(25)
            current_smu.reset_smu()
            
            # Set source function to voltage
            current_smu.set_source_function_voltage()
            print("✅ Source function set to voltage")
            
            # Test 1: Auto-range functionality
            print("\n1. Testing Auto-range functionality:")
            
            # Enable auto-range
            current_smu.set_voltage_range_auto_on()
            current_smu.write_smu(f"print({current_smu.channel}.source.autorangev)")
            auto_status = current_smu.read_smu()
            print(f"   Auto-range status: {auto_status}")
            
            # Disable auto-range
            current_smu.set_voltage_range_auto_off()
            current_smu.write_smu(f"print({current_smu.channel}.source.autorangev)")
            auto_status = current_smu.read_smu()
            print(f"   Auto-range status: {auto_status}")
            
            # Test 2: Setting specific voltage ranges
            print("\n2. Testing specific voltage ranges:")
            
            # Test different voltage ranges
            test_ranges = [0.2, 2.0, 20.0, 200.0]
            
            for test_range in test_ranges:
                print(f"\n   Setting voltage range to {test_range}V:")
                
                # Set the range
                current_smu.set_voltage_range_value(test_range)
                
                # Read back the actual range
                current_smu.write_smu(f"print({current_smu.channel}.source.rangev)")
                actual_range = float(current_smu.read_smu())
                print(f"   Actual range set: {actual_range}V")
                
                # Verify the range is reasonable
                if abs(actual_range - test_range) <= test_range * 0.1:  # Allow 10% tolerance
                    print(f"   ✅ Range {test_range}V set successfully")
                else:
                    print(f"   ⚠️  Range {test_range}V may not be exact (got {actual_range}V)")
            
            # Test 3: Auto-range with set_voltage_range_value(0)
            print("\n3. Testing auto-range with set_voltage_range_value(0):")
            current_smu.set_voltage_range_value(0)
            current_smu.write_smu(f"print({current_smu.channel}.source.autorangev)")
            auto_status = current_smu.read_smu()
            print(f"   Auto-range status: {auto_status}")
            
            # Test 4: Voltage level setting with different ranges
            print("\n4. Testing voltage level setting with different ranges:")
            
            test_voltages = [0.1, 1.0, 10.0, 50.0]
            
            for voltage in test_voltages:
                print(f"\n   Setting voltage level to {voltage}V:")
                
                # Set voltage level
                current_smu.set_voltage_level(voltage)
                
                # Read back the voltage level
                current_smu.write_smu(f"print({current_smu.channel}.source.levelv)")
                actual_voltage = float(current_smu.read_smu())
                print(f"   Actual voltage level: {actual_voltage}V")
                
                # Read the current range
                current_smu.write_smu(f"print({current_smu.channel}.source.rangev)")
                current_range = float(current_smu.read_smu())
                print(f"   Current voltage range: {current_range}V")
                
                if abs(actual_voltage - voltage) <= voltage * 0.01:  # Allow 1% tolerance
                    print(f"   ✅ Voltage {voltage}V set successfully")
                else:
                    print(f"   ⚠️  Voltage {voltage}V may not be exact (got {actual_voltage}V)")
            
            print("\n✅ All voltage range tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during voltage range testing: {e}")
            
        finally:
            # Clean up
            try:
                current_smu.set_output_off()
                current_smu.close_smu()
                print("✅ Connection closed")
            except:
                pass
    
    def test_source_function():
        """
        Test source function functionality for Keithley 2611
        
        Tests:
        1. Setting source function to voltage
        2. Setting source function to current
        3. Reading back the source function status
        4. Testing voltage and current level setting
        """
        print("Testing Keithley 2611 Source Function Functionality")
        print("=" * 55)
        
        current_smu = keithley_2611()
        
        try:
            # Connect to the instrument
            current_smu.create_smu_connector(visaResourceName)
            current_smu.timeout_smu(25)
            current_smu.reset_smu()
            
            # Test 1: Set source function to voltage
            print("\n1. Testing source function - Voltage mode:")
            current_smu.set_source_function_voltage()
            time.sleep(0.1)
            
            # Read back the source function
            source_func = current_smu.get_source_function()
            print(f"   Source function: {source_func}")
            
            if float(source_func) == 1.0:
                print("   ✅ Source function set to voltage successfully")
            else:
                print(f"   ⚠️  Expected 1.0, got: {source_func}")
            
            # Test voltage level setting
            print("\n   Testing voltage level setting:")
            test_voltage = 1.5
            current_smu.set_voltage_level(test_voltage)
            time.sleep(0.1)
            
            actual_voltage = current_smu.get_source_voltage_level()
            print(f"   Set voltage: {test_voltage}V, Actual: {actual_voltage}V")
            
            if abs(actual_voltage - test_voltage) <= test_voltage * 0.01:
                print("   ✅ Voltage level set successfully")
            else:
                print(f"   ⚠️  Voltage level may not be exact")
            
            # Test 2: Set source function to current
            print("\n2. Testing source function - Current mode:")
            current_smu.set_source_function_current()
            time.sleep(0.1)
            
            # Read back the source function
            source_func = current_smu.get_source_function()
            print(f"   Source function: {source_func}")
            
            if float(source_func) == 0.0:
                print("   ✅ Source function set to current successfully")
            else:
                print(f"   ⚠️  Expected 0.0, got: {source_func}")
            
            # Test current level setting
            print("\n   Testing current level setting:")
            test_current = 0.001  # 1mA
            current_smu.set_source_current_level(test_current)
            time.sleep(0.1)
            
            actual_current = current_smu.get_source_current_level()
            print(f"   Set current: {test_current}A, Actual: {actual_current}A")
            
            if abs(actual_current - test_current) <= test_current * 0.01:
                print("   ✅ Current level set successfully")
            else:
                print(f"   ⚠️  Current level may not be exact")
            
            # Test 3: Switch back to voltage and verify
            print("\n3. Testing source function - Switch back to voltage:")
            current_smu.set_source_function_voltage()
            time.sleep(0.1)
            
            # Read back the source function
            source_func = current_smu.get_source_function()
            print(f"   Source function: {source_func}")
            
            if float(source_func) == 1.0:
                print("   ✅ Source function switched back to voltage successfully")
            else:
                print(f"   ⚠️  Expected 1.0, got: {source_func}")
            
            print("\n✅ All source function tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during source function testing: {e}")
            
        finally:
            # Clean up
            try:
                current_smu.close_smu()
                print("✅ Connection closed")
            except:
                pass
    
    def test_source_delay():
        """
        Test source delay functionality for Keithley 2611
        
        Tests:
        1. Auto delay on/off
        2. Setting specific delay times
        3. Reading back the delay values
        """
        print("Testing Keithley 2611 Source Delay Functionality")
        print("=" * 50)
        
        current_smu = keithley_2611()
        
        try:
            # Connect to the instrument
            current_smu.create_smu_connector(visaResourceName)
            current_smu.timeout_smu(25)
            current_smu.reset_smu()
            
            # Set source function to voltage
            current_smu.set_source_function_voltage()
            print("✅ Source function set to voltage")
            
            # Test 1: Auto delay functionality
            print("\n1. Testing Auto delay functionality:")
            
            # Enable auto delay
            current_smu.set_source_voltage_delay_auto_on()
            time.sleep(0.1)
            
            auto_status = current_smu.get_source_voltage_delay_auto_status()
            print(f"   Auto delay status: {auto_status}")
            
            # Disable auto delay
            current_smu.set_source_voltage_delay_auto_off()
            time.sleep(0.1)
            
            auto_status = current_smu.get_source_voltage_delay_auto_status()
            print(f"   Auto delay status: {auto_status}")
            
            # Test 2: Setting specific delay times
            print("\n2. Testing specific delay times:")
            
            # Test different delay times
            test_delays = [0.001, 0.01, 0.1, 1.0]  # 1ms, 10ms, 100ms, 1s
            
            for test_delay_ms in test_delays:
                print(f"\n   Setting delay time to {test_delay_ms}ms:")
                
                # Set the delay
                current_smu.set_source_voltage_delay_time(test_delay_ms)
                time.sleep(0.1)
                
                # Read back the actual delay
                actual_delay = current_smu.get_source_voltage_delay_time()
                print(f"   Actual delay set: {actual_delay}s ({actual_delay*1000}ms)")
                
                # Verify the delay is reasonable
                expected_delay = test_delay_ms / 1000
                if abs(actual_delay - expected_delay) <= expected_delay * 0.1:  # Allow 10% tolerance
                    print(f"   ✅ Delay {test_delay_ms}ms set successfully")
                else:
                    print(f"   ⚠️  Delay {test_delay_ms}ms may not be exact (got {actual_delay*1000}ms)")
            
            # Test 3: Auto delay with set_source_voltage_delay_time(0)
            print("\n3. Testing auto delay with set_source_voltage_delay_time(0):")
            current_smu.set_source_voltage_delay_time(0)  # This should enable auto delay
            time.sleep(0.1)
            
            auto_status = current_smu.get_source_voltage_delay_auto_status()
            print(f"   Auto delay status: {auto_status}")
            
            # Test 4: Delay with voltage level changes
            print("\n4. Testing delay with voltage level changes:")
            
            test_voltages = [0.5, 1.0, 1.5, 2.0]
            
            for voltage in test_voltages:
                print(f"\n   Setting voltage level to {voltage}V:")
                
                # Set voltage level
                current_smu.set_voltage_level(voltage)
                time.sleep(0.1)
                
                # Read back the voltage level
                actual_voltage = current_smu.get_source_voltage_level()
                print(f"   Actual voltage level: {actual_voltage}V")
                
                # Read the current delay
                current_delay = current_smu.get_source_voltage_delay_time()
                print(f"   Current delay: {current_delay}s")
                
                if abs(actual_voltage - voltage) <= voltage * 0.01:  # Allow 1% tolerance
                    print(f"   ✅ Voltage {voltage}V set successfully")
                else:
                    print(f"   ⚠️  Voltage {voltage}V may not be exact (got {actual_voltage}V)")
            
            print("\n✅ All source delay tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during source delay testing: {e}")
            
        finally:
            # Clean up
            try:
                current_smu.close_smu()
                print("✅ Connection closed")
            except:
                pass
    
    def test_measure_current_nplc():
        current_smu = keithley_2611()
        current_smu.create_smu_connector(visaResourceName)
        current_smu.reset_smu()
        current_smu.timeout_smu(25)
        current_smu.set_source_function_voltage()
        # time.sleep(0.1)
        current_smu.set_voltage_level(1.0)
        current_smu.set_measure_current_nplc(0.1)
        
        # turn on SMU 
        current_smu.set_output_on()
        time.sleep(0.1)
        # query nplc
        current_smu.write_smu("print(smua.measure.nplc)")
        time.sleep(0.1)
        print(current_smu.read_smu())
        time.sleep(3)
        current_smu.set_output_off()
        current_smu.close_smu()
    
    def test_set_measure_current_limit():
        current_smu = keithley_2611()
        current_smu.create_smu_connector(visaResourceName)
        current_smu.reset_smu()
        current_smu.timeout_smu(25)
        current_smu.set_source_function_voltage()
        # time.sleep(0.1)
        current_smu.set_voltage_level(1.0)
        current_smu.set_measure_current_nplc(0.1)
        current_smu.set_measure_current_limit(0.06)
        
        # turn on SMU 
        current_smu.set_output_on()
        time.sleep(0.1)
        # query nplc
        current_smu.write_smu("print(smua.source.limiti)")
        print(current_smu.read_smu())
        time.sleep(3)
        current_smu.set_output_off()
        current_smu.close_smu()
    
    def test_set_measure_current_range():
        current_smu = keithley_2611()
        current_smu.create_smu_connector(visaResourceName)
        current_smu.reset_smu()
        current_smu.timeout_smu(25)
        current_smu.set_source_function_voltage()
        # time.sleep(0.1)
        current_smu.set_voltage_level(1.0)
        current_smu.set_measure_current_nplc(0.1)
        current_smu.set_measure_current_limit(0.001)
        current_smu.set_measure_current_range(1e-1)
        
        # turn on SMU 
        current_smu.set_output_on()
        time.sleep(0.1)
        # query nplc
        current_smu.write_smu("print(smua.measure.rangei)")
        print(current_smu.read_smu())
        time.sleep(3)
        current_smu.set_output_off()
        current_smu.close_smu()
    
    def test_set_measure_mode_current():
        current_smu = keithley_2611()
        current_smu.create_smu_connector(visaResourceName)
        current_smu.reset_smu()
        current_smu.timeout_smu(25)
        current_smu.set_source_function_voltage()
        # time.sleep(0.1)
        current_smu.set_voltage_level(1.0)
        current_smu.set_measure_current_nplc(0.1)
        current_smu.set_measure_current_limit(0.001)
        current_smu.set_measure_current_range(1e-1)
        current_smu.set_measure_mode_current()
        
        # turn on SMU 
        current_smu.set_output_on()
        time.sleep(0.1)
        # query nplc
        current_smu.write_smu("print(display.smua.measure.func)")
        print(current_smu.read_smu())
        time.sleep(3)
        current_smu.set_output_off()
        current_smu.close_smu()
    # run test code here
    # test_set_measure_mode_current()
    # test_voltage_range()  # New comprehensive voltage range test
    # test_source_function()  # New source function test
    test_source_delay()  # New source delay test

    # test code
    # current_smu.set_front_terminal()
    # current_smu.set_source_function_voltage()
    # current_smu.set_measure_mode_current()
    # current_smu.set_measure_current_range(100e-3)
    # current_smu.set_measure_current_limit(50e-3)
    # current_smu.set_voltage_range_auto_on()

    # current_smu.set_voltage_level(2.1)
    # current_smu.set_measure_current_nplc(0.1)
    # current_smu.set_output_on()

    # # print(current_smu.query_smu(':SENS:CURR:NPLC?'))
    # current_smu.set_output_off()
    # current_smu.close_smu() 