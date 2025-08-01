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
        
        # Apply the loaded configuration to the dialog components
        self.apply_config_to_dialog()
        
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
        self.measure_mode_combo.activated.connect(self.measure_mode_changed)

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

    def measure_mode_changed(self):
        # Change the tab based on the measurement mode
        if self.measure_mode_combo.currentText() == 'IV':
            self.tabs_IV_RT.setCurrentIndex(0)
        elif self.measure_mode_combo.currentText() == 'RT':
            self.tabs_IV_RT.setCurrentIndex(1)
    
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
    def load_settings(self, setting_window: qtc.QSettings, setting_variable: qtc.QSettings):
        pass
        # from View
        # try:
        #     self.resize(setting_window.value('window_size'))
        #     self.move(setting_window.value('window_position'))
        #     # user interface parameters
        #     self.visa_name.setCurrentText(setting_variable.value('visa_name'))
        #     self.terminal_value.setCurrentText(setting_variable.value('terminal'))
        #     self.nplc_value.setCurrentText(setting_variable.value('nplc'))
        #     self.measure_mode_combo.setCurrentText(setting_variable.value('mea_mode'))
        #     self.tabs_IV_RT.setCurrentIndex(self.measure_mode_combo.currentData())

        #     # # IV Parameters
        #     self.source_delay_time_value.setText(setting_variable.value('sour_delay_time'))
        #     self.voltage_range_combo.setCurrentText(setting_variable.value('v_range'))
        #     self.from_voltage_value.setText(setting_variable.value('from_v'))
        #     self.to_voltage_value.setText(setting_variable.value('to_v'))
        #     self.step_voltage_value.setText(setting_variable.value('step_v'))
        #     self.current_range_combo.setCurrentText(setting_variable.value('i_range'))

        #     # RT parameters
        #     self.rt_voltage_range_combo.setCurrentText(setting_variable.value('rt_v_range'))
        #     self.rt_voltage_set_value.setText(setting_variable.value('rt_v_set'))
        #     self.rt_current_range_combo.setCurrentText(setting_variable.value('rt_i_range'))
        #     self.rt_aperture_value.setText(setting_variable.value('aperture'))

        #     # # file and Plot Dialog
        #     self.folder_location_text.setText(setting_variable.value('save_folder'))
        #     self.file_name_text.setText(setting_variable.value('file_name'))
        #     self.log_linear_combo.setCurrentText(setting_variable.value('y_scale'))

        #     # set current parameter correspondingly
        #     self.yscale = self.log_linear_combo.currentText()
        #     self.meas_mode = self.measure_mode_combo.currentText()

        # except Exception as e:
        #     print(f"View Error loading settings: {e}")
    
    def apply_config_to_dialog(self):
        """Apply the loaded configuration to the dialog components"""
        try:
            # Apply global settings
            if 'visa_name' in self.config['global']:
                self.visa_name.setCurrentText(self.config['global']['visa_name'])
            if 'terminal' in self.config['global']:
                terminal_value = self.config['global']['terminal']
                for i in range(self.terminal_value.count()):
                    if self.terminal_value.itemData(i) == terminal_value:
                        self.terminal_value.setCurrentIndex(i)
                        break
            if 'nplc' in self.config['global']:
                nplc_value = self.config['global']['nplc']
                for i in range(self.nplc_value.count()):
                    if self.nplc_value.itemData(i) == nplc_value:
                        self.nplc_value.setCurrentIndex(i)
                        break
            if 'meas_mode' in self.config['global']:
                self.measure_mode_combo.setCurrentText(self.config['global']['meas_mode'])
            
            # Apply IV settings
            if 'source_delay_ms' in self.config['IV']:
                self.source_delay_time_value.setText(str(self.config['IV']['source_delay_ms']))
            if 'voltage_range' in self.config['IV']:
                voltage_range = self.config['IV']['voltage_range']
                for i in range(self.voltage_range_combo.count()):
                    if self.voltage_range_combo.itemData(i) == voltage_range:
                        self.voltage_range_combo.setCurrentIndex(i)
                        break
            if 'startV' in self.config['IV']:
                self.from_voltage_value.setText(str(self.config['IV']['startV']))
            if 'stopV' in self.config['IV']:
                self.to_voltage_value.setText(str(self.config['IV']['stopV']))
            if 'stepV' in self.config['IV']:
                self.step_voltage_value.setText(str(self.config['IV']['stepV']))
            if 'current_range' in self.config['IV']:
                current_range = self.config['IV']['current_range']
                for i in range(self.current_range_combo.count()):
                    if self.current_range_combo.itemData(i) == current_range:
                        self.current_range_combo.setCurrentIndex(i)
                        break
            
            # Apply RT settings
            if 'rt_voltage_range' in self.config['RT']:
                rt_voltage_range = self.config['RT']['rt_voltage_range']
                for i in range(self.rt_voltage_range_combo.count()):
                    if self.rt_voltage_range_combo.itemData(i) == rt_voltage_range:
                        self.rt_voltage_range_combo.setCurrentIndex(i)
                        break
            if 'rt_voltage_set' in self.config['RT']:
                self.rt_voltage_set_value.setText(str(self.config['RT']['rt_voltage_set']))
            if 'rt_current_range' in self.config['RT']:
                rt_current_range = self.config['RT']['rt_current_range']
                for i in range(self.rt_current_range_combo.count()):
                    if self.rt_current_range_combo.itemData(i) == rt_current_range:
                        self.rt_current_range_combo.setCurrentIndex(i)
                        break
            if 'rt_aperture' in self.config['RT']:
                self.rt_aperture_value.setText(str(self.config['RT']['rt_aperture']))
            
            # Apply file and plot settings
            if 'save_folder' in self.config['global']:
                self.folder_location_text.setText(self.config['global']['save_folder'])
            if 'file_name' in self.config['global']:
                self.file_name_text.setText(self.config['global']['file_name'])
            if 'y_scale' in self.config['global']:
                self.log_linear_combo.setCurrentText(self.config['global']['y_scale'])
                
        except Exception as e:
            print(f"Error applying config to dialog: {e}")

    def save_settings(self, setting_window: qtc.QSettings, setting_variable: qtc.QSettings):
        pass
        # from View
        # setting_window.setValue('window_size', self.size())
        # setting_window.setValue('window_position', self.pos())

        # # user interface parameters
        # setting_variable.setValue('visa_name', self.visa_name.currentText())
        # setting_variable.setValue('terminal', self.terminal_value.currentText())
        # setting_variable.setValue('nplc', self.nplc_value.currentText())
        # setting_variable.setValue('mea_mode', self.measure_mode_combo.currentText())
        # #
        # # # IV Parameters
        # setting_variable.setValue('sour_delay_time', self.source_delay_time_value.text())
        # setting_variable.setValue('v_range', self.voltage_range_combo.currentText())
        # setting_variable.setValue('from_v', self.from_voltage_value.text())
        # setting_variable.setValue('to_v', self.to_voltage_value.text())
        # setting_variable.setValue('step_v', self.source_delay_time_value.text())
        # setting_variable.setValue('i_range', self.current_range_combo.currentText())

        # # # RT parameters
        # setting_variable.setValue('rt_v_range', self.rt_voltage_range_combo.currentText())
        # setting_variable.setValue('rt_v_set', self.rt_voltage_set_value.text())
        # setting_variable.setValue('rt_i_range', self.rt_current_range_combo.currentText())
        # setting_variable.setValue('aperture', self.rt_aperture_value.text())
        # #
        # # # file and Plot Dialog
        # setting_variable.setValue('save_folder', self.folder_location_text.text())
        # setting_variable.setValue('file_name', self.file_name_text.text())
        # setting_variable.setValue('y_scale', self.log_linear_combo.currentText())