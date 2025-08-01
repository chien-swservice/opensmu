# view/main_view.py
from PyQt5 import QtWidgets as qtw, QtCore as qtc
from PyQt5.QtCore import Qt
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
        _layout = qtw.QHBoxLayout(self)
        self.left_layout = qtw.QVBoxLayout()
        self.right_layout = qtw.QVBoxLayout()

        _layout.addLayout(self.left_layout)
        _layout.addLayout(self.right_layout)

        # left layout = file dialog and communication box
        spacer01 = qtw.QSpacerItem(20, 100, qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Minimum)
        # create configuration dialog
        self.left_layout.addItem(spacer01)
        _button_layout = qtw.QVBoxLayout()
        self.configure_button = qtw.QPushButton('Configuration')
        self.configure_button.setFixedSize(200, 40)     
        _button_layout.addWidget(self.configure_button, alignment=Qt.AlignCenter)    
        self.clear_graph_button = qtw.QPushButton('Clear Graph')
        self.clear_graph_button.setFixedSize(200, 40)
        _button_layout.addWidget(self.clear_graph_button, alignment=Qt.AlignCenter)

        self.start_button = qtw.QPushButton('start')
        self.stop_button = qtw.QPushButton('stop')
        self.exit_button = qtw.QPushButton('exit')
        self.start_button.setFixedSize(200, 40)
        self.stop_button.setFixedSize(200, 40)
        self.exit_button.setFixedSize(200, 40)
        _button_layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        _button_layout.addWidget(self.stop_button, alignment=Qt.AlignCenter)
        _button_layout.addWidget(self.exit_button, alignment=Qt.AlignCenter)
        _button_layout.setSpacing(30)

        self.left_layout.addLayout(_button_layout)
        
        spacer = qtw.QSpacerItem(20, 200, qtw.QSizePolicy.Minimum, qtw.QSizePolicy.Minimum)
        self.left_layout.addItem(spacer)
        self._build_communication_box()
        # create right layout widgets
        self._right_layout_widgets()       

    def _right_layout_widgets(self):
        # right layout = graph and buttons
        self.figure = plt.figure(figsize=(120, 60))
        self.canvas = FigureCanvas(self.figure)
        _toolbar = NavigationToolbar(self.canvas, self)
        
        self.right_layout.addWidget(_toolbar)
        self.right_layout.addWidget(self.canvas)

    def _build_communication_box(self):
        _communication_box = qtw.QGroupBox('Communication')
        _communication_box.setMinimumHeight(300)
        _communication_box.setMinimumWidth(400)
        _communication_layout = qtw.QVBoxLayout()
        _communication_box.setLayout(_communication_layout)
        self.communication_text = qtw.QTextEdit()
        _communication_layout.addWidget(self.communication_text)

        self.left_layout.addWidget(_communication_box)
    
    def load_settings(self, setting_window: qtc.QSettings):
        # load settings from setting_window

        try:
            self.resize(setting_window.value('window_size'))
            self.move(setting_window.value('window_position'))
            # user interface parameters

        except Exception as e:
            print(f"View Error loading settings: {e}")

    def save_settings(self, setting_window: qtc.QSettings):
        setting_window.setValue('window_size', self.size())
        setting_window.setValue('window_position', self.pos())

    def message(self, msg):
        self.communication_text.append(msg)
        
    def closeEvent(self, event):
        print("Close event triggered")
        self.closeSignal.emit()
        event.accept()
