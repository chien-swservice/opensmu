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