# view/main_view.py
from PyQt5 import QtWidgets as qtw, QtCore as qtc
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import pyvisa
import os

class View(qtw.QWidget):
    closeSignal = qtc.pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Source Measurement Units realtimeIV')
        self.resize(2400, 1800)

        # main layout = left and right layout
        self.layout = qtw.QHBoxLayout(self)
        self.left_layout = qtw.QVBoxLayout()
        self.right_layout = qtw.QVBoxLayout()

        self.layout.addLayout(self.left_layout)
        self.layout.addLayout(self.right_layout)

        # left layout = file dialog and communication box    
        self._build_smu_box()
        self._build_iv_rt_tab()
        self._build_file_dialog_box()
        self._build_communication_box()
        # create right layout widgets
        self._right_layout_widgets()       

    def _right_layout_widgets(self):
        # right layout = graph and buttons
        self.figure = plt.figure(figsize=(120, 60))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.start_button = qtw.QPushButton('start')
        self.stop_button = qtw.QPushButton('stop')
        self.exit_button = qtw.QPushButton('exit')

        self.right_layout.addWidget(self.toolbar)
        self.right_layout.addWidget(self.canvas)

        btn_layout = qtw.QHBoxLayout()
        btn_layout.addItem(qtw.QSpacerItem(0, 0, qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Minimum))
        btn_layout.addWidget(self.start_button)
        btn_layout.addWidget(self.stop_button)
        btn_layout.addWidget(self.exit_button)
        self.right_layout.addLayout(btn_layout)

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

        self.left_layout.addWidget(self.smu_box)

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

        self.left_layout.addWidget(self.tabs_IV_RT)
    def _build_file_dialog_box(self):
        # File dialog GroupBox
        self.fileDialog_box = qtw.QGroupBox('File and Plot Dialog', alignment=qtc.Qt.AlignHCenter, flat=True)
        self.fileDialog_box.setStyleSheet('QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center; padding-left: 10px; padding-right: 10px;}')
        self.fileDialog_layout = qtw.QGridLayout()
        self.fileDialog_box.setLayout(self.fileDialog_layout)

        # File location Label
        folder_location_label = qtw.QLabel('File Location')
        self.search_folder_button = qtw.QPushButton('Folder')
        self.folder_location_text = qtw.QLineEdit(os.getcwd())
        
        # File name
        file_name_label = qtw.QLabel('File Name')
        self.file_name_text = qtw.QLineEdit('data')
        
        graph_yscale = qtw.QLabel('y-scale')
        self.log_linear_combo = qtw.QComboBox()
        self.log_linear_combo.addItems(['linear', 'log'])
        self.sw_version_label = qtw.QLabel('Software version:')
        self.clear_graph_button = qtw.QPushButton('Clear Graph')

        self.fileDialog_layout.addWidget(folder_location_label, 1, 1)
        self.fileDialog_layout.addWidget(self.folder_location_text, 2, 2, 1, 3)
        self.fileDialog_layout.addWidget(self.search_folder_button, 2, 1)
        self.fileDialog_layout.addWidget(file_name_label, 3, 1)
        self.fileDialog_layout.addWidget(self.file_name_text, 3, 3)
        self.fileDialog_layout.addWidget(graph_yscale, 4, 1)
        self.fileDialog_layout.addWidget(self.log_linear_combo, 4, 3)
        self.fileDialog_layout.addWidget(self.clear_graph_button, 5, 3)
        self.fileDialog_layout.addWidget(self.sw_version_label, 6, 1)

        self.left_layout.addWidget(self.fileDialog_box)

    def _build_communication_box(self):
        self.communication_box = qtw.QGroupBox('Communication')
        self.communication_layout = qtw.QVBoxLayout()
        self.communication_box.setLayout(self.communication_layout)
        self.communication_text = qtw.QTextEdit()
        self.communication_layout.addWidget(self.communication_text)

        self.left_layout.addWidget(self.communication_box)
    
    def load_settings(self, setting_window: qtc.QSettings, setting_variable: qtc.QSettings):
        # load settings from setting_window and setting_variable

        try:
            self.resize(setting_window.value('window_size'))
            self.move(setting_window.value('window_position'))
            # user interface parameters
            self.visa_name.setCurrentText(setting_variable.value('visa_name'))
            self.terminal_value.setCurrentText(setting_variable.value('terminal'))
            self.nplc_value.setCurrentText(setting_variable.value('nplc'))
            self.measure_mode_combo.setCurrentText(setting_variable.value('mea_mode'))
            self.tabs_IV_RT.setCurrentIndex(self.measure_mode_combo.currentData())

            # # IV Parameters
            self.source_delay_time_value.setText(setting_variable.value('sour_delay_time'))
            self.voltage_range_combo.setCurrentText(setting_variable.value('v_range'))
            self.from_voltage_value.setText(setting_variable.value('from_v'))
            self.to_voltage_value.setText(setting_variable.value('to_v'))
            self.step_voltage_value.setText(setting_variable.value('step_v'))
            self.current_range_combo.setCurrentText(setting_variable.value('i_range'))

            # RT parameters
            self.rt_voltage_range_combo.setCurrentText(setting_variable.value('rt_v_range'))
            self.rt_voltage_set_value.setText(setting_variable.value('rt_v_set'))
            self.rt_current_range_combo.setCurrentText(setting_variable.value('rt_i_range'))
            self.rt_aperture_value.setText(setting_variable.value('aperture'))

            # # file and Plot Dialog
            self.folder_location_text.setText(setting_variable.value('save_folder'))
            self.file_name_text.setText(setting_variable.value('file_name'))
            self.log_linear_combo.setCurrentText(setting_variable.value('y_scale'))

            # set current parameter correspondingly
            self.yscale = self.log_linear_combo.currentText()
            self.meas_mode = self.measure_mode_combo.currentText()

        except Exception as e:
            print(f"View Error loading settings: {e}")

    def save_settings(self, setting_window: qtc.QSettings, setting_variable: qtc.QSettings):
        setting_window.setValue('window_size', self.size())
        setting_window.setValue('window_position', self.pos())

        # user interface parameters
        setting_variable.setValue('visa_name', self.visa_name.currentText())
        setting_variable.setValue('terminal', self.terminal_value.currentText())
        setting_variable.setValue('nplc', self.nplc_value.currentText())
        setting_variable.setValue('mea_mode', self.measure_mode_combo.currentText())
        #
        # # IV Parameters
        setting_variable.setValue('sour_delay_time', self.source_delay_time_value.text())
        setting_variable.setValue('v_range', self.voltage_range_combo.currentText())
        setting_variable.setValue('from_v', self.from_voltage_value.text())
        setting_variable.setValue('to_v', self.to_voltage_value.text())
        setting_variable.setValue('step_v', self.step_voltage_value.text())
        setting_variable.setValue('i_range', self.current_range_combo.currentText())

        # # RT parameters
        setting_variable.setValue('rt_v_range', self.rt_voltage_range_combo.currentText())
        setting_variable.setValue('rt_v_set', self.rt_voltage_set_value.text())
        setting_variable.setValue('rt_i_range', self.rt_current_range_combo.currentText())
        setting_variable.setValue('aperture', self.rt_aperture_value.text())
        #
        # # file and Plot Dialog
        setting_variable.setValue('save_folder', self.folder_location_text.text())
        setting_variable.setValue('file_name', self.file_name_text.text())
        setting_variable.setValue('y_scale', self.log_linear_combo.currentText())

    def closeEvent(self, event):
        print("Close event triggered")
        self.closeSignal.emit()
        event.accept()
    
    

