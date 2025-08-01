from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc   

class IVSettingsWidget(qtw.QWidget):
    """Widget for IV measurement settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = qtw.QFormLayout()
        self.setLayout(self.layout)
        
        # Source delay time
        self.source_delay_time_label = qtw.QLabel('Sour. Delay Time (ms)')
        self.source_delay_time_value = qtw.QLineEdit()
        self.source_delay_time_value.setText('50')
        
        # Voltage range
        self.voltage_range_label = qtw.QLabel('V range')
        self.voltage_range_combo = qtw.QComboBox()
        self.voltage_range_combo.addItem('Auto', 0)
        self.voltage_range_combo.addItem('20mV', 0.02)
        self.voltage_range_combo.addItem('200mV', 0.2)
        self.voltage_range_combo.addItem('2V', 2)
        self.voltage_range_combo.addItem('20V', 20)
        self.voltage_range_combo.addItem('200V', 200)
        self.voltage_range_combo.setCurrentText('2V')

        # Voltage sweep parameters
        self.from_voltage_label = qtw.QLabel('from V')
        self.from_voltage_value = qtw.QLineEdit()
        self.from_voltage_value.setText('-1')
        
        self.to_voltage_label = qtw.QLabel('to V')
        self.to_voltage_value = qtw.QLineEdit()
        self.to_voltage_value.setText('1')
        
        self.step_voltage_label = qtw.QLabel('step V')
        self.step_voltage_value = qtw.QLineEdit()
        self.step_voltage_value.setText('0.1')

        # Current range
        self.current_range_label = qtw.QLabel('I range')
        self.current_range_combo = qtw.QComboBox()
        self.current_range_combo.addItem('10nA', 10e-9)
        self.current_range_combo.addItem('100nA', 100e-9)
        self.current_range_combo.addItem('1uA', 1e-6)
        self.current_range_combo.addItem('10uA', 10e-6)
        self.current_range_combo.addItem('100uA', 100e-6)
        self.current_range_combo.addItem('1mA', 1e-3)
        self.current_range_combo.addItem('10mA', 10e-3)
        self.current_range_combo.addItem('100mA', 100e-3)
        self.current_range_combo.addItem('1A', 1)
        self.current_range_combo.setCurrentText('100uA')
        
        # Layout
        self.layout.addRow(self.source_delay_time_label, self.source_delay_time_value)
        self.layout.addRow(self.voltage_range_label, self.voltage_range_combo)
        self.layout.addRow(self.from_voltage_label, self.from_voltage_value)
        self.layout.addRow(self.to_voltage_label, self.to_voltage_value)
        self.layout.addRow(self.step_voltage_label, self.step_voltage_value)
        self.layout.addRow(self.current_range_label, self.current_range_combo)
    
    def get_config(self):
        """Get the current configuration from the widget"""
        return {
            'source_delay_ms': float(self.source_delay_time_value.text()),
            'voltage_range': float(self.voltage_range_combo.currentData()),
            'startV': float(self.from_voltage_value.text()),
            'stopV': float(self.to_voltage_value.text()),
            'stepV': float(self.step_voltage_value.text()),
            'current_range': float(self.current_range_combo.currentData())
        }
    
    def apply_config(self, config):
        """Apply configuration to the widget"""
        try:
            if 'source_delay_ms' in config:
                self.source_delay_time_value.setText(str(config['source_delay_ms']))
            if 'voltage_range' in config:
                voltage_range = config['voltage_range']
                for i in range(self.voltage_range_combo.count()):
                    if self.voltage_range_combo.itemData(i) == voltage_range:
                        self.voltage_range_combo.setCurrentIndex(i)
                        break
            if 'startV' in config:
                self.from_voltage_value.setText(str(config['startV']))
            if 'stopV' in config:
                self.to_voltage_value.setText(str(config['stopV']))
            if 'stepV' in config:
                self.step_voltage_value.setText(str(config['stepV']))
            if 'current_range' in config:
                current_range = config['current_range']
                for i in range(self.current_range_combo.count()):
                    if self.current_range_combo.itemData(i) == current_range:
                        self.current_range_combo.setCurrentIndex(i)
                        break
        except Exception as e:
            print(f"Error applying config to IV settings: {e}") 