from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc   

class RTSettingsWidget(qtw.QWidget):
    """Widget for RT measurement settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = qtw.QFormLayout()
        self.setLayout(self.layout)
        
        # Voltage range
        self.rt_voltage_range_label = qtw.QLabel('V Range')
        self.rt_voltage_range_combo = qtw.QComboBox()
        self.rt_voltage_range_combo.addItem('Auto', 0)
        self.rt_voltage_range_combo.addItem('20mV', 0.02)
        self.rt_voltage_range_combo.addItem('200mV', 0.2)
        self.rt_voltage_range_combo.addItem('2V', 2)
        self.rt_voltage_range_combo.addItem('20V', 20)
        self.rt_voltage_range_combo.addItem('200V', 200)
        self.rt_voltage_range_combo.setCurrentText('2V')

        # Voltage set point
        self.rt_voltage_set_label = qtw.QLabel('V set')
        self.rt_voltage_set_value = qtw.QLineEdit()
        self.rt_voltage_set_value.setText('0.5')

        # Current range
        self.rt_current_range_label = qtw.QLabel('I Range')
        self.rt_current_range_combo = qtw.QComboBox()
        self.rt_current_range_combo.addItem('10nA', 10e-9)
        self.rt_current_range_combo.addItem('100nA', 100e-9)
        self.rt_current_range_combo.addItem('1uA', 1e-6)
        self.rt_current_range_combo.addItem('10uA', 10e-6)
        self.rt_current_range_combo.addItem('100uA', 100e-6)
        self.rt_current_range_combo.addItem('1mA', 1e-3)
        self.rt_current_range_combo.addItem('10mA', 10e-3)
        self.rt_current_range_combo.addItem('100mA', 100e-3)
        self.rt_current_range_combo.addItem('1A', 1)
        self.rt_current_range_combo.setCurrentText('100uA')

        # Aperture time
        self.rt_aperture_label = qtw.QLabel('Aperture (s)')
        self.rt_aperture_value = qtw.QLineEdit()
        self.rt_aperture_value.setText('1')
        
        # Layout
        self.layout.addRow(self.rt_voltage_range_label, self.rt_voltage_range_combo)
        self.layout.addRow(self.rt_voltage_set_label, self.rt_voltage_set_value)
        self.layout.addRow(self.rt_current_range_label, self.rt_current_range_combo)
        self.layout.addRow(self.rt_aperture_label, self.rt_aperture_value)
    
    def get_config(self):
        """Get the current configuration from the widget"""
        return {
            'rt_voltage_range': float(self.rt_voltage_range_combo.currentData()),
            'rt_voltage_set': float(self.rt_voltage_set_value.text()),
            'rt_current_range': float(self.rt_current_range_combo.currentData()),
            'rt_aperture': float(self.rt_aperture_value.text())
        }
    
    def apply_config(self, config):
        """Apply configuration to the widget"""
        try:
            if 'rt_voltage_range' in config:
                rt_voltage_range = config['rt_voltage_range']
                for i in range(self.rt_voltage_range_combo.count()):
                    if self.rt_voltage_range_combo.itemData(i) == rt_voltage_range:
                        self.rt_voltage_range_combo.setCurrentIndex(i)
                        break
            if 'rt_voltage_set' in config:
                self.rt_voltage_set_value.setText(str(config['rt_voltage_set']))
            if 'rt_current_range' in config:
                rt_current_range = config['rt_current_range']
                for i in range(self.rt_current_range_combo.count()):
                    if self.rt_current_range_combo.itemData(i) == rt_current_range:
                        self.rt_current_range_combo.setCurrentIndex(i)
                        break
            if 'rt_aperture' in config:
                self.rt_aperture_value.setText(str(config['rt_aperture']))
        except Exception as e:
            print(f"Error applying config to RT settings: {e}") 