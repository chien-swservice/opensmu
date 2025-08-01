from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore as qtc   
from .smu_control_widget import SMUControlWidget
from .iv_settings_widget import IVSettingsWidget
from .rt_settings_widget import RTSettingsWidget
from .file_settings_widget import FileSettingsWidget

class ConfigDialog(qtw.QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration")
        self.resize(400, 600)

        self.config = config.copy()

        self.layout = qtw.QVBoxLayout()

        # Create modular widgets
        self._create_widgets()
        self._setup_layout()
        
        # Apply the loaded configuration to the dialog components
        self.apply_config_to_dialog()
        
        # Add OK/Cancel buttons
        self.buttonBox = qtw.QDialogButtonBox(qtw.QDialogButtonBox.Ok | qtw.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def _create_widgets(self):
        """Create all the modular widgets"""
        # SMU Control widget
        self.smu_widget = SMUControlWidget()
        self.smu_widget.measure_mode_combo.activated.connect(self.measure_mode_changed)
        
        # IV Settings widget
        self.iv_widget = IVSettingsWidget()
        
        # RT Settings widget
        self.rt_widget = RTSettingsWidget()
        
        # File Settings widget
        self.file_widget = FileSettingsWidget()
        
        # Create tab widget for IV/RT settings
        self.tabs_IV_RT = qtw.QTabWidget()
        self.tab_IV = qtw.QWidget()
        self.tab_RT = qtw.QWidget()
        self.tabs_IV_RT.addTab(self.tab_IV, 'IV')
        self.tabs_IV_RT.addTab(self.tab_RT, 'RT')
        
        # Add widgets to tabs
        self.tab_IV_layout = qtw.QVBoxLayout()
        self.tab_IV.setLayout(self.tab_IV_layout)
        self.tab_IV_layout.addWidget(self.iv_widget)
        
        self.tab_RT_layout = qtw.QVBoxLayout()
        self.tab_RT.setLayout(self.tab_RT_layout)
        self.tab_RT_layout.addWidget(self.rt_widget)

    def _setup_layout(self):
        """Setup the main layout"""
        # Add SMU Control widget
        self.layout.addWidget(self.smu_widget)
        
        # Add IV/RT tabs
        self.layout.addWidget(self.tabs_IV_RT)
        
        # Add File Settings widget
        self.layout.addWidget(self.file_widget)

    def measure_mode_changed(self):
        """Change the tab based on the measurement mode"""
        if self.smu_widget.measure_mode_combo.currentText() == 'IV':
            self.tabs_IV_RT.setCurrentIndex(0)
        elif self.smu_widget.measure_mode_combo.currentText() == 'RT':
            self.tabs_IV_RT.setCurrentIndex(1)

    def get_config(self):
        """Collect the configuration data from all widgets"""
        smu_config = self.smu_widget.get_config()
        iv_config = self.iv_widget.get_config()
        rt_config = self.rt_widget.get_config()
        file_config = self.file_widget.get_config()
        
        return {
            'IV': iv_config,
            'RT': rt_config,
            'global': {**smu_config, **file_config}
        }

    def load_settings(self, setting_window: qtc.QSettings):
        """Load settings (placeholder for future implementation)"""
        pass

    def apply_config_to_dialog(self):
        """Apply the loaded configuration to all dialog components"""
        try:
            # Apply to SMU widget
            self.smu_widget.apply_config(self.config['global'])
            
            # Apply to IV widget
            self.iv_widget.apply_config(self.config['IV'])
            
            # Apply to RT widget
            self.rt_widget.apply_config(self.config['RT'])
            
            # Apply to File widget
            self.file_widget.apply_config(self.config['global'])
            
        except Exception as e:
            print(f"Error applying config to dialog: {e}")

    def save_settings(self, setting_window: qtc.QSettings):
        """Save settings (placeholder for future implementation)"""
        pass
        