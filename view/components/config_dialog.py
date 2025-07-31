from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc   
import pyvisa
import os

class ConfigDialog(qtw.QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.resize(300, 150)

        self.config = config.copy()

        self.layout = qtw.QVBoxLayout()

        # load data from config here
        self._build_smu_box()
        self._build_iv_rt_tab()
        self._build_file_dialog_box()
        self.buttonBox = qtw.QDialogButtonBox(qtw.QDialogButtonBox.Ok | qtw.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def _build_smu_box(self):    
        # smu connect
        self.visa_label = qtw.QLabel('Visa name')
        self.visa_name = qtw.QComboBox()
        # create instance for connecting to the device
        self.rm = pyvisa.ResourceManager()
        self.instruments_list = self.rm.list_resources()
        for i in range(len(self.instruments_list)):
            item = self.instruments_list.__getitem__(i)
            if 'GPIB' in item:
                self.visa_name.addItem(item, i)
        # terminal
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
        
        # measurement mode
        self.measure_mode_label = qtw.QLabel('Mea. Mode')
        self.measure_mode_combo = qtw.QComboBox()
        self.measure_mode_combo.addItem('IV', 0)
        self.measure_mode_combo.addItem('RT', 1)
        self.measure_mode_combo.setCurrentText('IV')

        # smu box layout
        self.smu_box = qtw.QGroupBox('SMU Control', alignment=qtc.Qt.AlignHCenter, flat=True)
        self.smu_box.setStyleSheet('QGroupBox:title {'
                                        'subcontrol-origin: margin;'
                                        'subcontrol-position: top center;'
                                        'padding-left: 10px;'
                                        'padding-right: 10px;}')
        self.smu_layout = qtw.QGridLayout()
        self.smu_box.setLayout(self.smu_layout)
        self.smu_layout.addWidget(self.visa_label, 1, 1)
        self.smu_layout.addWidget(self.visa_name, 1, 2, 1, 3)
        self.smu_layout.addWidget(self.terminal_label, 2, 1)
        self.smu_layout.addWidget(self.terminal_value, 2, 3)
        self.smu_layout.addWidget(self.nplc_label, 3, 1)
        self.smu_layout.addWidget(self.nplc_value, 3, 3)
        self.smu_layout.addWidget(self.measure_mode_label, 4, 1)
        self.smu_layout.addWidget(self.measure_mode_combo, 4, 3)

        self.layout.addWidget(self.smu_box)

    def _build_iv_rt_tab(self):
        # parameter for IV measurement
        self.source_delay_time_label = qtw.QLabel('Sour. Delay Time (ms)')
        self.source_delay_time_value = qtw.QLineEdit()
        self.source_delay_time_value.setText('50')
        self.voltage_range_label = qtw.QLabel('V range')
        self.voltage_range_combo = qtw.QComboBox()
        self.voltage_range_combo.addItem('Auto', 0)
        self.voltage_range_combo.addItem('20mV', 0.02)
        self.voltage_range_combo.addItem('200mV', 0.2)
        self.voltage_range_combo.addItem('2V', 2)
        self.voltage_range_combo.addItem('20V', 20)
        self.voltage_range_combo.addItem('200V', 200)
        self.voltage_range_combo.setCurrentText('2V')

        self.from_voltage_label = qtw.QLabel('from V')
        self.from_voltage_value = qtw.QLineEdit()
        self.from_voltage_value.setText('-1')
        self.to_voltage_label = qtw.QLabel('to V')
        self.to_voltage_value = qtw.QLineEdit()
        self.to_voltage_value.setText('1')
        self.step_voltage_label = qtw.QLabel('step V')
        self.step_voltage_value = qtw.QLineEdit()
        self.step_voltage_value.setText('0.1')

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
        
        # parameter for RT measurements
        self.rt_voltage_range_label = qtw.QLabel('V Range')
        self.rt_voltage_range_combo = qtw.QComboBox()
        self.rt_voltage_range_combo.addItem('Auto', 0)
        self.rt_voltage_range_combo.addItem('20mV', 0.02)
        self.rt_voltage_range_combo.addItem('200mV', 0.2)
        self.rt_voltage_range_combo.addItem('2V', 2)
        self.rt_voltage_range_combo.addItem('20V', 20)
        self.rt_voltage_range_combo.addItem('200V', 200)
        self.rt_voltage_range_combo.setCurrentText('2V')

        self.rt_voltage_set_label = qtw.QLabel('V set')
        self.rt_voltage_set_value = qtw.QLineEdit()
        self.rt_voltage_set_value.setText('0.5')

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

        self.rt_aperture_label = qtw.QLabel('Aperture (s)')
        self.rt_aperture_value = qtw.QLineEdit()
        self.rt_aperture_value.setText('1')
        # and a tab here and move the items belongs to IV to the Tab1
        self.tabs_IV_RT = qtw.QTabWidget()
        self.tab_IV = qtw.QWidget()
        self.tab_RT = qtw.QWidget()
        self.tabs_IV_RT.addTab(self.tab_IV, 'IV')
        self.tabs_IV_RT.addTab(self.tab_RT, 'RT')
        # self.left_layout.addWidget(self.tabs_IV_RT)
        self.tab_IV_layout = qtw.QFormLayout()
        self.tab_IV.setLayout(self.tab_IV_layout)
        self.tab_IV_layout.addRow(self.source_delay_time_label, self.source_delay_time_value)
        self.tab_IV_layout.addRow(self.voltage_range_label, self.voltage_range_combo)
        self.tab_IV_layout.addRow(self.from_voltage_label, self.from_voltage_value)
        self.tab_IV_layout.addRow(self.to_voltage_label, self.to_voltage_value)
        self.tab_IV_layout.addRow(self.step_voltage_label, self.step_voltage_value)
        self.tab_IV_layout.addRow(self.current_range_label, self.current_range_combo)

        self.tab_RT_layout = qtw.QFormLayout()
        self.tab_RT.setLayout(self.tab_RT_layout)
        self.tab_RT_layout.addRow(self.rt_voltage_range_label, self.rt_voltage_range_combo)
        self.tab_RT_layout.addRow(self.rt_voltage_set_label, self.rt_voltage_set_value)
        self.tab_RT_layout.addRow(self.rt_current_range_label, self.rt_current_range_combo)
        self.tab_RT_layout.addRow(self.rt_aperture_label, self.rt_aperture_value)

        self.layout.addWidget(self.tabs_IV_RT)

    def _build_file_dialog_box(self):
        # File dialog GroupBox
        self.fileDialog_box = qtw.QGroupBox('File and Plot Dialog', alignment=qtc.Qt.AlignHCenter, flat=True)
        self.fileDialog_box.setStyleSheet('QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center; padding-left: 10px; padding-right: 10px;}')
        self.fileDialog_layout = qtw.QGridLayout()
        self.fileDialog_box.setLayout(self.fileDialog_layout)

        # File location Label
        folder_location_label = qtw.QLabel('File Location')
        self.search_folder_button = qtw.QPushButton('Folder')
        self.search_folder_button.clicked.connect(self.folder_clicked)
        self.folder_location_text = qtw.QLineEdit(os.path.join(os.getcwd(), 'data'))
        
        # File name
        file_name_label = qtw.QLabel('File Name')
        self.file_name_text = qtw.QLineEdit('data')
        graph_yscale = qtw.QLabel('y-scale')
        self.log_linear_combo = qtw.QComboBox()
        self.log_linear_combo.addItems(['linear', 'log'])

        self.fileDialog_layout.addWidget(folder_location_label, 1, 1)
        self.fileDialog_layout.addWidget(self.folder_location_text, 2, 2, 1, 3)
        self.fileDialog_layout.addWidget(self.search_folder_button, 2, 1)
        self.fileDialog_layout.addWidget(file_name_label, 3, 1)
        self.fileDialog_layout.addWidget(self.file_name_text, 3, 3)
        self.fileDialog_layout.addWidget(graph_yscale, 4, 1)
        self.fileDialog_layout.addWidget(self.log_linear_combo, 4, 3)

        self.layout.addWidget(self.fileDialog_box)

    def folder_clicked(self):
        # if data folder does not exist, create it
        if not os.path.exists(os.path.join(os.getcwd(), 'data')):
            os.makedirs(os.path.join(os.getcwd(), 'data'))

        currentLocation = qtw.QFileDialog.getExistingDirectory(
            self,
            caption='select a folder',
            directory=os.path.join(os.getcwd(), 'data')
        )
        self.folder_location_text.setText(currentLocation)

    def get_config(self):
        # Collecting the configuration data from the dialog
        return {
            'IV': {
                'source_delay_ms': float(self.source_delay_time_value.text()),
                'voltage_range': float(self.voltage_range_combo.currentData()),
                'startV': float(self.from_voltage_value.text()),
                'stopV': float(self.to_voltage_value.text()),
                'stepV': float(self.step_voltage_value.text()),
                'current_range': float(self.current_range_combo.currentData())
            },
            'RT': {
                'rt_voltage_range': float(self.rt_voltage_range_combo.currentData()),
                'rt_voltage_set': float(self.rt_voltage_set_value.text()),
                'rt_current_range': float(self.rt_current_range_combo.currentData()),
                'rt_aperture': float(self.rt_aperture_value.text())
            },
            'global': {
                'visa_name': self.visa_name.currentText(),
                'terminal': self.terminal_value.currentData(),
                'nplc': float(self.nplc_value.currentData()),
                'meas_mode': self.measure_mode_combo.currentText(),
                'save_folder': self.folder_location_text.text(),
                'file_name': self.file_name_text.text(),
                'y_scale': self.log_linear_combo.currentText()
            }
        }