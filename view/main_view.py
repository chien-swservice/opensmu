# view/main_view.py
from PyQt5 import QtWidgets as qtw, QtCore as qtc
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import os

class MainView(qtw.QWidget):
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

        # create right layout widgets
        self.right_layout_widgets()

        # left layout = file dialog and communication box

        self.folder_location_text = qtw.QLineEdit(os.getcwd())
        self.file_name_text = qtw.QLineEdit('data')
        self.communication_text = qtw.QTextEdit()

        self.log_linear_combo = qtw.QComboBox()
        self.log_linear_combo.addItems(['linear', 'log'])
        self.sw_version_label = qtw.QLabel('Software version:')
        self.clear_graph_button = qtw.QPushButton('Clear Graph')

        self._build_file_dialog_box()
        self._build_communication_box()

    def right_layout_widgets(self):
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

    def _build_file_dialog_box(self):
        self.fileDialog_box = qtw.QGroupBox('File and Plot Dialog', alignment=qtc.Qt.AlignHCenter, flat=True)
        self.fileDialog_box.setStyleSheet('QGroupBox:title {subcontrol-origin: margin; subcontrol-position: top center; padding-left: 10px; padding-right: 10px;}')
        self.fileDialog_layout = qtw.QGridLayout()
        self.fileDialog_box.setLayout(self.fileDialog_layout)

        folder_location_label = qtw.QLabel('File Location')
        search_folder_button = qtw.QPushButton('Folder')
        file_name_label = qtw.QLabel('File Name')
        graph_yscale = qtw.QLabel('y-scale')

        self.fileDialog_layout.addWidget(folder_location_label, 1, 1)
        self.fileDialog_layout.addWidget(self.folder_location_text, 2, 2, 1, 3)
        self.fileDialog_layout.addWidget(search_folder_button, 2, 1)
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
        self.communication_layout.addWidget(self.communication_text)
        self.left_layout.addWidget(self.communication_box)
