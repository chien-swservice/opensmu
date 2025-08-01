from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc   
import os

class FileSettingsWidget(qtw.QGroupBox):
    """Widget for file and plot settings"""
    
    def __init__(self, parent=None):
        super().__init__("File and Plot Dialog", parent)
        self.setAlignment(qtc.Qt.AlignHCenter)
        self.setFlat(True)
        self.setStyleSheet('QGroupBox:title {'
                                'subcontrol-origin: margin;'
                                'subcontrol-position: top center;'
                                'padding-left: 10px;'
                                'padding-right: 10px;}')
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface"""
        self.layout = qtw.QGridLayout()
        self.setLayout(self.layout)
        
        # File location
        folder_location_label = qtw.QLabel('File Location')
        self.search_folder_button = qtw.QPushButton('Folder')
        self.search_folder_button.clicked.connect(self.folder_clicked)
        self.folder_location_text = qtw.QLineEdit(os.path.join(os.getcwd(), 'data'))
        
        # File name
        file_name_label = qtw.QLabel('File Name')
        self.file_name_text = qtw.QLineEdit('data')
        
        # Y-scale
        graph_yscale = qtw.QLabel('y-scale')
        self.log_linear_combo = qtw.QComboBox()
        self.log_linear_combo.addItems(['linear', 'log'])

        # Layout
        self.layout.addWidget(folder_location_label, 1, 1)
        self.layout.addWidget(self.folder_location_text, 2, 2, 1, 3)
        self.layout.addWidget(self.search_folder_button, 2, 1)
        self.layout.addWidget(file_name_label, 3, 1)
        self.layout.addWidget(self.file_name_text, 3, 3)
        self.layout.addWidget(graph_yscale, 4, 1)
        self.layout.addWidget(self.log_linear_combo, 4, 3)
    
    def folder_clicked(self):
        """Handle folder selection button click"""
        # if data folder does not exist, create it
        if not os.path.exists(os.path.join(os.getcwd(), 'data')):
            os.makedirs(os.path.join(os.getcwd(), 'data'))

        currentLocation = qtw.QFileDialog.getExistingDirectory(
            self,
            caption='select a folder',
            directory=os.path.join(os.getcwd(), 'data')
        )
        if currentLocation:
            self.folder_location_text.setText(currentLocation)
    
    def get_config(self):
        """Get the current configuration from the widget"""
        return {
            'save_folder': self.folder_location_text.text(),
            'file_name': self.file_name_text.text(),
            'y_scale': self.log_linear_combo.currentText()
        }
    
    def apply_config(self, config):
        """Apply configuration to the widget"""
        try:
            if 'save_folder' in config:
                self.folder_location_text.setText(config['save_folder'])
            if 'file_name' in config:
                self.file_name_text.setText(config['file_name'])
            if 'y_scale' in config:
                self.log_linear_combo.setCurrentText(config['y_scale'])
        except Exception as e:
            print(f"Error applying config to file settings: {e}") 