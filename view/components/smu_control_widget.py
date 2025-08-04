from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc   
import pyvisa

class SMUControlWidget(qtw.QGroupBox):
    """Widget for SMU control settings"""
    
    def __init__(self, parent=None):
        super().__init__("SMU Control", parent)
        self.setAlignment(qtc.Qt.AlignHCenter)
        self.setFlat(True)
        self.setStyleSheet('QGroupBox:title {'
                                'subcontrol-origin: margin;'
                                'subcontrol-position: top center;'
                                'padding-left: 10px;'
                                'padding-right: 10px;}')
        
        self._init_ui()
        self._populate_instruments()
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = qtw.QGridLayout()
        self.setLayout(self.layout)
        
        # SMU Type selection
        self.smu_type_label = qtw.QLabel('SMU Type')
        self.smu_type_combo = qtw.QComboBox()
        self.smu_type_combo.addItem('SMU Simulation', 'simulation')
        self.smu_type_combo.addItem('Keithley 2450', 'keithley2450')
        self.smu_type_combo.addItem('Keithley 2611', 'keithley2611')
        self.smu_type_combo.addItem('Keithley 26xxAB', 'keithley26xxab')
        self.smu_type_combo.addItem('Keithley 24xx', 'keithley24xx')
        self.smu_type_combo.addItem('Agilent B2900', 'agilent_b2900')
        self.smu_type_combo.setCurrentText('SMU Simulation')
        
        # Visa name
        self.visa_label = qtw.QLabel('Visa name')
        self.visa_name = qtw.QComboBox()
        
        # Terminal
        self.terminal_label = qtw.QLabel('terminal')
        self.terminal_value = qtw.QComboBox()
        self.terminal_value.addItem('front', 'FRON')
        self.terminal_value.addItem('rear', 'REAR')

        # NPLC settings
        self.nplc_label = qtw.QLabel('nplc')
        self.nplc_value = qtw.QComboBox()
        self.nplc_value.addItem('Fast', 0.01)
        self.nplc_value.addItem('Medium', 0.10)
        self.nplc_value.addItem('Normal', 1.00)
        self.nplc_value.addItem('High Accuracy', 10.00)
        self.nplc_value.setCurrentText('Normal')
        
        # Measurement mode
        self.measure_mode_label = qtw.QLabel('Mea. Mode')
        self.measure_mode_combo = qtw.QComboBox()
        self.measure_mode_combo.addItem('IV', 0)
        self.measure_mode_combo.addItem('RT', 1)
        self.measure_mode_combo.setCurrentText('IV')
        
        # Test connection button
        self.test_connection_btn = qtw.QPushButton('Test Connection')
        self.test_connection_btn.clicked.connect(self._test_connection)
        
        # List devices button
        self.list_devices_btn = qtw.QPushButton('List Devices')
        self.list_devices_btn.clicked.connect(self._list_devices)
        
        # Layout
        self.layout.addWidget(self.smu_type_label, 0, 1)
        self.layout.addWidget(self.smu_type_combo, 0, 2, 1, 3)
        self.layout.addWidget(self.visa_label, 1, 1)
        self.layout.addWidget(self.visa_name, 1, 2, 1, 3)
        self.layout.addWidget(self.terminal_label, 2, 1)
        self.layout.addWidget(self.terminal_value, 2, 3)
        self.layout.addWidget(self.nplc_label, 3, 1)
        self.layout.addWidget(self.nplc_value, 3, 3)
        self.layout.addWidget(self.measure_mode_label, 4, 1)
        self.layout.addWidget(self.measure_mode_combo, 4, 3)
        self.layout.addWidget(self.test_connection_btn, 5, 1, 1, 2)
        self.layout.addWidget(self.list_devices_btn, 5, 3, 1, 2)
    
    def _populate_instruments(self):
        """Populate the instruments list with available GPIB devices"""
        try:
            self.rm = pyvisa.ResourceManager()
            self.instruments_list = self.rm.list_resources()
            for i in range(len(self.instruments_list)):
                item = self.instruments_list.__getitem__(i)
                if 'GPIB' in item:
                    self.visa_name.addItem(item, i)
        except Exception as e:
            print(f"Error populating instruments: {e}")
    
    def get_config(self):
        """Get the current configuration from the widget"""
        return {
            'smu_type': self.smu_type_combo.currentData(),
            'visa_name': self.visa_name.currentText(),
            'terminal': self.terminal_value.currentData(),
            'nplc': float(self.nplc_value.currentData()),
            'meas_mode': self.measure_mode_combo.currentText()
        }
    
    def apply_config(self, config):
        """Apply configuration to the widget"""
        try:
            if 'smu_type' in config:
                smu_type_value = config['smu_type']
                for i in range(self.smu_type_combo.count()):
                    if self.smu_type_combo.itemData(i) == smu_type_value:
                        self.smu_type_combo.setCurrentIndex(i)
                        break
            if 'visa_name' in config:
                self.visa_name.setCurrentText(config['visa_name'])
            if 'terminal' in config:
                terminal_value = config['terminal']
                for i in range(self.terminal_value.count()):
                    if self.terminal_value.itemData(i) == terminal_value:
                        self.terminal_value.setCurrentIndex(i)
                        break
            if 'nplc' in config:
                nplc_value = config['nplc']
                for i in range(self.nplc_value.count()):
                    if self.nplc_value.itemData(i) == nplc_value:
                        self.nplc_value.setCurrentIndex(i)
                        break
            if 'meas_mode' in config:
                self.measure_mode_combo.setCurrentText(config['meas_mode'])
        except Exception as e:
            print(f"Error applying config to SMU control: {e}")
    
    def _test_connection(self):
        """Test the current SMU connection"""
        from PyQt5.QtWidgets import QMessageBox
        
        smu_type = self.smu_type_combo.currentData()
        visa_name = self.visa_name.currentText()
        
        if smu_type == 'simulation':
            QMessageBox.information(self, "Connection Test", 
                                  "Simulation SMU - connection test passed!")
            return
        
        if not visa_name or visa_name.strip() == '':
            QMessageBox.warning(self, "Connection Test", 
                              "No VISA address configured!\n\nPlease select a valid VISA address.")
            return
        
        try:
            # Create a temporary SMU instance for testing
            if smu_type == 'keithley2450':
                from devices.keithley2450 import keithley_2450
                test_smu = keithley_2450()
            elif smu_type == 'keithley2611':
                from devices.keithley2611 import keithley_2611
                test_smu = keithley_2611()
            elif smu_type == 'keithley26xxab':
                from devices.keithley26xxab import keithley_26xxab
                test_smu = keithley_26xxab()
            elif smu_type == 'keithley24xx':
                from devices.keithley24xx import keithley_24xx
                test_smu = keithley_24xx()
            elif smu_type == 'agilent_b2900':
                from devices.agilent_b2900 import agilent_b2900
                test_smu = agilent_b2900()
            else:
                QMessageBox.warning(self, "Connection Test", 
                                  f"Unknown SMU type: {smu_type}")
                return
            
            # Test connection
            test_smu.create_smu_connector(visa_name)
            device_id = test_smu.identify_smu()
            test_smu.close_smu()
            
            QMessageBox.information(self, "Connection Test", 
                                  f"✅ Connection successful!\n\nDevice ID:\n{device_id.strip()}")
            
        except Exception as e:
            error_msg = str(e)
            if "VI_ERROR_RSRC_NFOUND" in error_msg:
                message = f"❌ Device not found at {visa_name}\n\nPossible causes:\n• Device is not powered on\n• Device is not connected\n• VISA address is incorrect\n• GPIB/USB driver not installed"
            elif "VI_ERROR_RSRC_BUSY" in error_msg:
                message = f"❌ Device at {visa_name} is busy\n\nAnother application may be using the device"
            elif "VI_ERROR_TMO" in error_msg:
                message = f"❌ Connection timeout to {visa_name}\n\nDevice may be slow to respond or not ready"
            else:
                message = f"❌ Connection failed to {visa_name}\n\nError: {error_msg}"
            
            QMessageBox.critical(self, "Connection Test", message)
    
    def _list_devices(self):
        """List all available VISA devices"""
        from PyQt5.QtWidgets import QMessageBox
        import pyvisa
        
        try:
            rm = pyvisa.ResourceManager()
            resources = rm.list_resources()
            
            if not resources:
                QMessageBox.information(self, "Available Devices", 
                                      "No VISA devices found.\n\nMake sure your devices are:\n• Powered on\n• Connected to the computer\n• Have proper drivers installed")
                return
            
            device_list = "\n".join([f"{i+1}. {resource}" for i, resource in enumerate(resources)])
            message = f"Found {len(resources)} VISA device(s):\n\n{device_list}"
            
            QMessageBox.information(self, "Available Devices", message)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to list VISA devices:\n{str(e)}") 