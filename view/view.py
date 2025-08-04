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
    
    def plot_rt(self, x_vals, y_vals, y_scale='linear', x_alldata=None, y_alldata=None):
        print("call plot_rt")
        """Plot real-time measurement data"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Configure plot settings
        ax.grid(which='major', color='grey', linewidth=1)
        ax.grid(which='minor', color='darkgrey', linestyle=':', linewidth=0.8)
        ax.minorticks_on()
        
        plt.title("Real-time measurement", fontsize=20, fontweight='bold')
        plt.xlabel("time (s)", fontsize=18, fontweight='bold')
        plt.ylabel("current (A)", fontsize=18, fontweight='bold')
        plt.rcParams['xtick.labelsize'] = 16
        plt.rcParams['ytick.labelsize'] = 16
        
        # Set y-scale
        if y_scale == 'log':
            ax.set_yscale('log')
            plt.ylabel("|current| (A)", fontsize=18, fontweight='bold')
        
        # Define colors for different curves
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        # Plot previous measurements (history) with different colors and transparency
        if x_alldata and y_alldata and len(x_alldata) > 0:
            for i in range(len(x_alldata)):
                if i < len(x_alldata) and i < len(y_alldata):
                    if y_scale == 'log':
                        plot_y_vals = [abs(y) for y in y_alldata[i]]
                    else:
                        plot_y_vals = y_alldata[i]
                    color = colors[i % len(colors)]
                    # Higher transparency for older measurements
                    alpha = max(0.2, 0.8 - (i * 0.1))
                    ax.plot(x_alldata[i], plot_y_vals, color=color, linewidth=1.5, alpha=alpha, 
                           marker='o', markersize=3, label=f'Run {i+1}')
        
        
        # Plot current data
        if x_vals and y_vals:
            if y_scale == 'log':
                plot_y_vals = [abs(y) for y in y_vals]
            else:
                plot_y_vals = y_vals
            current_color = colors[len(x_alldata) % len(colors)] if x_alldata else 'blue'
            ax.plot(x_vals, plot_y_vals, color=current_color, linewidth=2.5, alpha=1.0, 
                   marker='o', markersize=4, label='Current')
        
        # Add legend if there are multiple curves
        if (x_alldata and len(x_alldata) > 0) or (x_vals and len(x_vals) > 0):
            ax.legend()
        
        # Update canvas
        self.canvas.draw()
        
    def plot_iv(self, x_vals, y_vals, y_scale='linear', x_alldata=None, y_alldata=None):
        """Plot IV measurement data"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        # Configure plot settings
        ax.grid(which='major', color='grey', linewidth=1)
        ax.grid(which='minor', color='darkgrey', linestyle=':', linewidth=0.8)
        ax.minorticks_on()
        
        plt.title("IV measurement", fontsize=20)
        plt.xlabel("voltage (V)", fontsize=18)
        plt.ylabel("current (A)", fontsize=18)
        plt.rcParams['xtick.labelsize'] = 16
        plt.rcParams['ytick.labelsize'] = 16
        
        # Set y-scale
        if y_scale == 'log':
            ax.set_yscale('log')
            plt.ylabel("|current| (A)", fontsize=18)
        
        # Define colors for different curves
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
        
        # Plot previous measurements (history) with different colors and transparency
        if x_alldata and y_alldata:
            for i in range(len(x_alldata)):
                if y_scale == 'log':
                    plot_y_vals = [abs(y) for y in y_alldata[i]]
                else:
                    plot_y_vals = y_alldata[i]
                color = colors[i % len(colors)]
                # Higher transparency for older measurements
                alpha = max(0.2, 0.8 - (i * 0.1))
                ax.plot(x_alldata[i], plot_y_vals, color=color, linewidth=1.5, alpha=alpha, 
                       marker='o', markersize=3, label=f'Run {i+1}')
        
        # Plot current data
        if x_vals and y_vals:
            if y_scale == 'log':
                plot_y_vals = [abs(y) for y in y_vals]
            else:
                plot_y_vals = y_vals
            current_color = colors[len(x_alldata) % len(colors)] if x_alldata else 'red'
            ax.plot(x_vals, plot_y_vals, color=current_color, linewidth=2.5, alpha=1.0, 
                   marker='o', markersize=4, label='Current')
        
        # Add legend if there are multiple curves
        if (x_alldata and len(x_alldata) > 0) or (x_vals and len(x_vals) > 0):
            ax.legend()
        
        # Update canvas
        self.canvas.draw()
    
    def clear_plot(self):
        """Clear the plot"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.grid(True)
        self.canvas.draw()
        
    def closeEvent(self, event):
        print("Close event triggered")
        self.closeSignal.emit()
        event.accept()
