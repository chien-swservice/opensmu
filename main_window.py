from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc
from view.view import View

class MainWindow(qtw.QWidget):
    def __init__(self):    
        super().__init__()
        self.view = View()
        self.settings_init()
        self.connect_signals()
        self.view.show()

    def settings_init(self):
        self.setting_window = qtc.QSettings('KeithleyIV_RT', 'windows size')
        self.setting_variable = qtc.QSettings('KeithleyIV_RT', 'user interface')
        # self.timer = qtc.QTimer()
        # self.timer.timeout.connect(self.timeOutEvent)
        # load saved settings into the view
        self.view.load_settings(self.setting_window, self.setting_variable)

    def connect_signals(self):
        # Connect signals to slots here
        self.view.start_button.clicked.connect(self.start_clicked)
        self.view.stop_button.clicked.connect(self.stop_clicked)
        self.view.exit_button.clicked.connect(self.exit_clicked)

        # measurement mode change
        self.view.measure_mode_combo.activated.connect(self.measure_mode_changed)
        # search folder button
        self.view.search_folder_button.clicked.connect(self.folder_clicked)
        # clear graph button
        self.view.clear_graph_button.clicked.connect(self.clear_graph_clicked)

        # Connect close event
        self.view.closeSignal.connect(self.on_view_closed)


    def start_clicked(self):
        # Start button logic
        print("Start button clicked")
        

    def stop_clicked(self):
        # Stop button logic
        print("Stop button clicked")

    def exit_clicked(self):
        # Exit button logic
        print("Exit button clicked")
    
    def measure_mode_changed(self):
        pass
    
    def folder_clicked(self):
        pass

    def clear_graph_clicked(self):
        # Clear graph logic
        print("Clear graph button clicked")

    def on_view_closed(self):
        self.view.save_settings(self.setting_window, self.setting_variable)
        # self.view.close()
        print("MainView closed")
        
    


    