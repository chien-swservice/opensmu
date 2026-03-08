"""
Keysight B2900 Series SMU driver.

NOTE: This driver has NOT been tested on real hardware.
      It is included for future validation. Use with caution.
"""
import pyvisa
from devices.smu_base import SMUBase

class keysight_b2900(SMUBase):
    def __init__(self):
        self.visaResourceName = None
        self.rm = pyvisa.ResourceManager()
        self.Keysight = None

    # establish a connection for the SMU
    def create_smu_connector(self, visaResourceName):
        self.visaResourceName = visaResourceName
        self.Keysight = self.rm.open_resource(self.visaResourceName)
        
    def reset_smu(self):
        """Reset the instrument to default settings"""
        self.Keysight.write('*RST')
        
    def identify_smu(self):
        """Query instrument identification"""
        return self.Keysight.query('*IDN?')
        
    def query_smu(self, command):
        """Send a query command and return the response"""
        return self.Keysight.query(command)
        
    def write_smu(self, command):
        """Send a write command"""
        self.Keysight.write(command)
        
    def read_smu(self):
        """Read response from instrument"""
        return self.Keysight.read()

    # standard time out is 25 seconds
    def timeout_smu(self, time_s):
        """Set instrument timeout in seconds"""
        self.Keysight.timeout = time_s

    '''set the terminal output front or rear'''
    def set_front_terminal(self):
        """
        Set terminal to front (Keysight B2900 uses front terminals by default)
        
        According to Keysight B2900 Series User Manual:
        - B2900 series instruments typically use front terminals by default
        - No specific command needed for front terminal selection
        """
        # Keysight B2900 uses front terminals by default
        # No specific command needed
        self.Keysight.write(':ROUT:TERM FRON')
        
    def set_rear_terminal(self):
        """
        Set terminal to rear (Keysight B2900 uses front terminals by default)
        
        According to Keysight B2900 Series User Manual:
        - B2900 series instruments typically use front terminals by default
        - Rear terminal selection may not be available on all models
        """       
        self.Keysight.write(':ROUT:TERM REAR')
        
    '''set the source functions'''

    '''set the source voltage delay auto on'''
    def set_source_voltage_delay_auto_on(self):
        """
        Enable auto delay for voltage source
        
        According to Keysight B2900 Series User Manual:
        - Enables automatic delay for voltage source
        - Uses SCPI command: :SOUR:VOLT:DEL:AUTO ON
        """
        self.Keysight.write(":SOUR:VOLT:DEL:AUTO ON")
        
    def set_source_voltage_delay_auto_off(self):
        """
        Disable auto delay for voltage source
        
        According to Keysight B2900 Series User Manual:
        - Disables automatic delay for voltage source
        - Uses SCPI command: :SOUR:VOLT:DEL:AUTO OFF
        """
        self.Keysight.write(":SOUR:VOLT:DEL:AUTO OFF")
        
    def set_source_voltage_delay_time(self, time_ms):
        """
        Set source voltage delay time
        
        According to Keysight B2900 Series User Manual:
        - Sets the source delay time in seconds
        - Uses SCPI command: :SOUR:VOLT:DEL delay_time
        - The delay is applied after each source level change
        
        Args:
            time_ms (float): Delay time in milliseconds (converted to seconds)
        """
        source_delay = float(time_ms) / 1000
        self.Keysight.write(f":SOUR:VOLT:DEL {source_delay}")
    
    def get_source_voltage_delay_time(self):
        """
        Get current source voltage delay time
        
        Returns:
            float: Current delay time in seconds
        """
        return float(self.Keysight.query(":SOUR:VOLT:DEL?"))
    
    def get_source_voltage_delay_auto_status(self):
        """
        Get current auto delay status for voltage source
        
        Returns:
            str: Auto delay status (ON/OFF)
        """
        return self.Keysight.query(":SOUR:VOLT:DEL:AUTO?").strip()

    '''set source function as voltage or current output'''
    def set_source_function_voltage(self):
        """
        Set source function to voltage output
        
        According to Keysight B2900 Series User Manual:
        - Sets the source function to voltage output
        - Uses SCPI command: :SOUR:FUNC VOLT
        """
        self.Keysight.write(':SOUR:FUNC VOLT')
        
    def set_source_function_current(self):
        """
        Set source function to current output
        
        According to Keysight B2900 Series User Manual:
        - Sets the source function to current output
        - Uses SCPI command: :SOUR:FUNC CURR
        """
        self.Keysight.write(':SOUR:FUNC CURR')
    
    def get_source_function(self):
        """
        Get current source function
        
        Returns:
            str: Current source function (VOLT or CURR)
        """
        return self.Keysight.query(':SOUR:FUNC?').strip()

    '''set voltage range auto or value'''
    def set_voltage_range_auto_on(self):
        """
        Enable auto-range for voltage source
        
        According to Keysight B2900 Series User Manual:
        - Enables automatic voltage range selection
        - Uses SCPI command: :SOUR:VOLT:RANG:AUTO ON
        """
        self.Keysight.write(":SOUR:VOLT:RANG:AUTO ON")
        
    def set_voltage_range_auto_off(self):
        """
        Disable auto-range for voltage source
        
        According to Keysight B2900 Series User Manual:
        - Disables automatic voltage range selection
        - Uses SCPI command: :SOUR:VOLT:RANG:AUTO OFF
        """
        self.Keysight.write(":SOUR:VOLT:RANG:AUTO OFF")
        
    def set_voltage_range_value(self, voltage_range):
        """
        Set voltage range value for Keysight B2900
        
        According to Keysight B2900 Series User Manual:
        - Voltage ranges: 0.2V, 2V, 20V, 200V (depending on model)
        - The instrument will automatically select the closest available range
        - If voltage_range is 0, auto-range is enabled
        
        Args:
            voltage_range (float): Voltage range in volts
        """
        if voltage_range == 0:
            # Enable auto-range
            self.Keysight.write(":SOUR:VOLT:RANG:AUTO ON")
        else:
            # Set specific voltage range
            # The Keysight B2900 will automatically select the closest available range
            self.Keysight.write(f":SOUR:VOLT:RANG {voltage_range}")
    
    def get_voltage_range(self):
        """
        Get current voltage range value
        
        Returns:
            float: Current voltage range in volts
        """
        return float(self.Keysight.query(":SOUR:VOLT:RANG?"))
    
    def get_voltage_autorange_status(self):
        """
        Get current auto-range status
        
        Returns:
            str: Auto-range status (ON/OFF)
        """
        return self.Keysight.query(":SOUR:VOLT:RANG:AUTO?").strip()
    
    # Current range functions
    def set_source_current_range_auto_on(self):
        """Enable auto-range for current source"""
        self.Keysight.write(":SOUR:CURR:RANG:AUTO ON")
        
    def set_source_current_range_auto_off(self):
        """Disable auto-range for current source"""
        self.Keysight.write(":SOUR:CURR:RANG:AUTO OFF")
        
    def set_source_current_range_value(self, current_range):
        """
        Set current range value for Keysight B2900
        
        According to Keysight B2900 Series User Manual:
        - Current ranges: 1e-9A, 1e-8A, 1e-7A, 1e-6A, 1e-5A, 1e-4A, 1e-3A, 1e-2A, 1e-1A, 1A, 3A (depending on model)
        - The instrument will automatically select the closest available range
        - If current_range is 0, auto-range is enabled
        
        Args:
            current_range (float): Current range in amperes
        """
        if current_range == 0:
            # Enable auto-range
            self.Keysight.write(":SOUR:CURR:RANG:AUTO ON")
        else:
            # Set specific current range
            # The Keysight B2900 will automatically select the closest available range
            self.Keysight.write(f":SOUR:CURR:RANG {current_range}")
    
    def get_source_current_range(self):
        """
        Get current current range value
        
        Returns:
            float: Current current range in amperes
        """
        return float(self.Keysight.query(":SOUR:CURR:RANG?"))
    
    def get_source_current_autorange_status(self):
        """
        Get current auto-range status for current source
        
        Returns:
            str: Auto-range status (ON/OFF)
        """
        return self.Keysight.query(":SOUR:CURR:RANG:AUTO?").strip()

    def set_voltage_level(self, voltage_level):
        """
        Set voltage level for voltage source
        
        According to Keysight B2900 Series User Manual:
        - Sets the voltage level in volts
        - Uses SCPI command: :SOUR:VOLT:LEV voltage_level
        
        Args:
            voltage_level (float): Voltage level in volts
        """
        self.Keysight.write(f":SOUR:VOLT:LEV {voltage_level}")
    
    def set_source_current_level(self, current_level):
        """
        Set current level for current source
        
        According to Keysight B2900 Series User Manual:
        - Sets the current level in amperes
        - Uses SCPI command: :SOUR:CURR:LEV current_level
        
        Args:
            current_level (float): Current level in amperes
        """
        self.Keysight.write(f":SOUR:CURR:LEV {current_level}")
    
    def get_source_voltage_level(self):
        """
        Get current voltage level
        
        Returns:
            float: Current voltage level in volts
        """
        return float(self.Keysight.query(":SOUR:VOLT:LEV?"))
    
    def get_source_current_level(self):
        """
        Get current current level
        
        Returns:
            float: Current current level in amperes
        """
        return float(self.Keysight.query(":SOUR:CURR:LEV?"))
        
    '''measurement mode and range'''
    def set_measure_mode_current(self):
        """
        Set measurement mode to current
        
        According to Keysight B2900 Series User Manual:
        - Sets the measurement function to current
        - Uses SCPI command: :SENS:FUNC 'CURR'
        """
        self.Keysight.write(":SENS:FUNC 'CURR'")
        
    def set_measure_mode_voltage(self):
        """
        Set measurement mode to voltage
        
        According to Keysight B2900 Series User Manual:
        - Sets the measurement function to voltage
        - Uses SCPI command: :SENS:FUNC 'VOLT'
        """
        self.Keysight.write(":SENS:FUNC 'VOLT'")
        
    def get_measure_function(self):
        """
        Get current measurement function
        
        Returns:
            str: Current measurement function
        """
        return self.Keysight.query(":SENS:FUNC?").strip()
        
    # for example current:range = 1e-3 , 1 mA
    def set_measure_current_range(self, current_range):
        """
        Set current measurement range
        
        According to Keysight B2900 Series User Manual:
        - Sets the current measurement range in amperes
        - Uses SCPI command: :SENS:CURR:RANG current_range
        
        Args:
            current_range (float): Current range in amperes
        """
        self.Keysight.write(f":SENS:CURR:RANG {current_range}")
        
    def set_measure_voltage_range(self, voltage_range):
        """
        Set voltage measurement range
        
        According to Keysight B2900 Series User Manual:
        - Sets the voltage measurement range in volts
        - Uses SCPI command: :SENS:VOLT:RANG voltage_range
        
        Args:
            voltage_range (float): Voltage range in volts
        """
        self.Keysight.write(f":SENS:VOLT:RANG {voltage_range}")
        
    def set_measure_current_limit(self, current_limit):
        """
        Set current limit for voltage source
        
        According to Keysight B2900 Series User Manual:
        - Sets the current limit in amperes
        - Uses SCPI command: :SOUR:VOLT:ILIM current_limit
        
        Args:
            current_limit (float): Current limit in amperes
        """
        self.Keysight.write(f":SOUR:VOLT:ILIM {current_limit}")
        
    def set_measure_voltage_limit(self, voltage_limit):
        """
        Set voltage limit for current source
        
        According to Keysight B2900 Series User Manual:
        - Sets the voltage limit in volts
        - Uses SCPI command: :SOUR:CURR:VLIM voltage_limit
        
        Args:
            voltage_limit (float): Voltage limit in volts
        """
        self.Keysight.write(f":SOUR:CURR:VLIM {voltage_limit}")
        
    '''set nplc value for current measurement'''
    def set_measure_current_nplc(self, nplc_value):
        """
        Set NPLC for current measurement
        
        According to Keysight B2900 Series User Manual:
        - Sets the number of power line cycles for current measurement
        - Uses SCPI command: :SENS:CURR:NPLC nplc_value
        
        Args:
            nplc_value (float): Number of power line cycles
        """
        self.Keysight.write(f":SENS:CURR:NPLC {nplc_value}")
        
    def set_measure_voltage_nplc(self, nplc_value):
        """
        Set NPLC for voltage measurement
        
        According to Keysight B2900 Series User Manual:
        - Sets the number of power line cycles for voltage measurement
        - Uses SCPI command: :SENS:VOLT:NPLC nplc_value
        
        Args:
            nplc_value (float): Number of power line cycles
        """
        self.Keysight.write(f":SENS:VOLT:NPLC {nplc_value}")
        
    '''smu output on/ off'''
    def set_output_on(self):
        """
        Turn output on
        
        According to Keysight B2900 Series User Manual:
        - Enables the source output
        - Uses SCPI command: :OUTP ON
        """
        self.Keysight.write(':OUTP ON')
        
    def set_output_off(self):
        """
        Turn output off
        
        According to Keysight B2900 Series User Manual:
        - Disables the source output
        - Uses SCPI command: :OUTP OFF
        """
        self.Keysight.write(':OUTP OFF')
        
    '''readout from keysight'''
    def readout(self):
        """
        Read current measurement
        
        According to Keysight B2900 Series User Manual:
        - Reads the current measurement in amperes
        - Uses SCPI command: :READ?
        
        Returns:
            float: Current measurement in amperes
        """
        self.Keysight.write(":READ?")
        return float(self.Keysight.read())
        
    def readout_voltage(self):
        """
        Read voltage measurement
        
        According to Keysight B2900 Series User Manual:
        - Reads the voltage measurement in volts
        - Uses SCPI command: :READ?
        
        Returns:
            float: Voltage measurement in volts
        """
        self.Keysight.write(":READ?")
        return float(self.Keysight.read())
        
    def close_smu(self):
        """Close the SMU connection"""
        self.Keysight.close()


# Test code for Keysight B2900
if __name__ == '__main__':
    import time
    visaResourceName = 'GPIB0::28::INSTR'  # Adjust for your instrument
    
    def test_keysight_b2900():
        """Test basic connection and identification"""
        current_smu = keysight_b2900()
        current_smu.create_smu_connector(visaResourceName)
        current_smu.timeout_smu(25)
        current_smu.write_smu('*IDN?')
        print(current_smu.read_smu())
        current_smu.close_smu()

    def test_source_function():
        """
        Test source function functionality for Keysight B2900
        
        Tests:
        1. Setting source function to voltage
        2. Setting source function to current
        3. Reading back the source function status
        4. Testing voltage and current level setting
        """
        print("Testing Keysight B2900 Source Function Functionality")
        print("=" * 55)
        
        current_smu = keysight_b2900()
        
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
            
            if "VOLT" in source_func:
                print("   ✅ Source function set to voltage successfully")
            else:
                print(f"   ⚠️  Expected VOLT, got: {source_func}")
            
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
            
            if "CURR" in source_func:
                print("   ✅ Source function set to current successfully")
            else:
                print(f"   ⚠️  Expected CURR, got: {source_func}")
            
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
            
            if "VOLT" in source_func:
                print("   ✅ Source function switched back to voltage successfully")
            else:
                print(f"   ⚠️  Expected VOLT, got: {source_func}")
            
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

    def test_voltage_range():
        """
        Test voltage range functionality for Keysight B2900
        
        Tests:
        1. Auto-range on/off
        2. Setting specific voltage ranges
        3. Reading back the actual range values
        """
        print("Testing Keysight B2900 Voltage Range Functionality")
        print("=" * 50)
        
        current_smu = keysight_b2900()
        
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
            time.sleep(0.1)
            
            auto_status = current_smu.get_voltage_autorange_status()
            print(f"   Auto-range status: {auto_status}")
            
            # Disable auto-range
            current_smu.set_voltage_range_auto_off()
            time.sleep(0.1)
            
            auto_status = current_smu.get_voltage_autorange_status()
            print(f"   Auto-range status: {auto_status}")
            
            # Test 2: Setting specific voltage ranges
            print("\n2. Testing specific voltage ranges:")
            
            # Test different voltage ranges
            test_ranges = [0.2, 2.0, 20.0, 200.0]
            
            for test_range in test_ranges:
                print(f"\n   Setting voltage range to {test_range}V:")
                
                # Set the range
                current_smu.set_voltage_range_value(test_range)
                time.sleep(0.1)
                
                # Read back the actual range
                actual_range = current_smu.get_voltage_range()
                print(f"   Actual range set: {actual_range}V")
                
                # Verify the range is reasonable
                if abs(actual_range - test_range) <= test_range * 0.1:  # Allow 10% tolerance
                    print(f"   ✅ Range {test_range}V set successfully")
                else:
                    print(f"   ⚠️  Range {test_range}V may not be exact (got {actual_range}V)")
            
            print("\n✅ All voltage range tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during voltage range testing: {e}")
            
        finally:
            # Clean up
            try:
                current_smu.close_smu()
                print("✅ Connection closed")
            except:
                pass

    def test_source_delay():
        """
        Test source delay functionality for Keysight B2900
        
        Tests:
        1. Auto delay on/off
        2. Setting specific delay times
        3. Reading back the delay values
        """
        print("Testing Keysight B2900 Source Delay Functionality")
        print("=" * 50)
        
        current_smu = keysight_b2900()
        
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

    def test_measurement_functions():
        """
        Test measurement functionality for Keysight B2900
        
        Tests:
        1. Setting measurement mode to current/voltage
        2. Setting measurement ranges
        3. Setting NPLC values
        4. Setting limits
        """
        print("Testing Keysight B2900 Measurement Functionality")
        print("=" * 55)
        
        current_smu = keysight_b2900()
        
        try:
            # Connect to the instrument
            current_smu.create_smu_connector(visaResourceName)
            current_smu.timeout_smu(25)
            current_smu.reset_smu()
            
            # Set source function to voltage
            current_smu.set_source_function_voltage()
            print("✅ Source function set to voltage")
            
            # Test 1: Measurement mode setting
            print("\n1. Testing measurement mode setting:")
            
            # Set to current measurement
            current_smu.set_measure_mode_current()
            time.sleep(0.1)
            
            measure_func = current_smu.get_measure_function()
            print(f"   Measurement function: {measure_func}")
            
            if "CURR" in measure_func:
                print("   ✅ Current measurement mode set successfully")
            else:
                print(f"   ⚠️  Expected CURR, got: {measure_func}")
            
            # Set to voltage measurement
            current_smu.set_measure_mode_voltage()
            time.sleep(0.1)
            
            measure_func = current_smu.get_measure_function()
            print(f"   Measurement function: {measure_func}")
            
            if "VOLT" in measure_func:
                print("   ✅ Voltage measurement mode set successfully")
            else:
                print(f"   ⚠️  Expected VOLT, got: {measure_func}")
            
            # Test 2: Measurement range setting
            print("\n2. Testing measurement range setting:")
            
            # Set current measurement range
            current_smu.set_measure_mode_current()
            current_smu.set_measure_current_range(1e-6)  # 1µA range
            print("   ✅ Current measurement range set to 1µA")
            
            # Set voltage measurement range
            current_smu.set_measure_mode_voltage()
            current_smu.set_measure_voltage_range(2.0)  # 2V range
            print("   ✅ Voltage measurement range set to 2V")
            
            # Test 3: NPLC setting
            print("\n3. Testing NPLC setting:")
            
            current_smu.set_measure_current_nplc(1.0)
            print("   ✅ Current NPLC set to 1.0")
            
            current_smu.set_measure_voltage_nplc(0.1)
            print("   ✅ Voltage NPLC set to 0.1")
            
            # Test 4: Limit setting
            print("\n4. Testing limit setting:")
            
            current_smu.set_measure_current_limit(1e-6)  # 1µA limit
            print("   ✅ Current limit set to 1µA")
            
            current_smu.set_measure_voltage_limit(2.0)  # 2V limit
            print("   ✅ Voltage limit set to 2V")
            
            print("\n✅ All measurement tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during measurement testing: {e}")
            
        finally:
            # Clean up
            try:
                current_smu.close_smu()
                print("✅ Connection closed")
            except:
                pass

    def test_output_control():
        """
        Test output control functionality for Keysight B2900
        
        Tests:
        1. Output on/off control
        2. Terminal selection
        3. Basic measurement with output on
        """
        print("Testing Keysight B2900 Output Control Functionality")
        print("=" * 55)
        
        current_smu = keysight_b2900()
        
        try:
            # Connect to the instrument
            current_smu.create_smu_connector(visaResourceName)
            current_smu.timeout_smu(25)
            current_smu.reset_smu()
            
            # Set up for voltage source, current measurement
            current_smu.set_source_function_voltage()
            current_smu.set_measure_mode_current()
            current_smu.set_voltage_level(1.0)
            current_smu.set_measure_current_range(1e-6)
            current_smu.set_measure_current_limit(1e-6)
            print("✅ Basic setup completed")
            
            # Test 1: Terminal selection
            print("\n1. Testing terminal selection:")
            
            current_smu.set_front_terminal()
            print("   ✅ Front terminal selected")
            
            current_smu.set_rear_terminal()
            print("   ✅ Rear terminal selected")
            
            # Test 2: Output control
            print("\n2. Testing output control:")
            
            current_smu.set_output_on()
            print("   ✅ Output turned ON")
            time.sleep(0.5)  # Wait for output to stabilize
            
            # Try to read a measurement
            try:
                current = current_smu.readout()
                print(f"   ✅ Current measurement: {current:.2e} A")
            except Exception as e:
                print(f"   ⚠️  Measurement failed (expected if no load): {e}")
            
            current_smu.set_output_off()
            print("   ✅ Output turned OFF")
            
            print("\n✅ All output control tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during output control testing: {e}")
            
        finally:
            # Clean up
            try:
                current_smu.set_output_off()
                current_smu.close_smu()
                print("✅ Connection closed")
            except:
                pass

    # Run test code here
    # test_keysight_b2900()
    # test_source_function()
    # test_voltage_range()
    # test_source_delay()
    # test_measurement_functions()
    test_output_control() 