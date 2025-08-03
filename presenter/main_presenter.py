"""
Main Presenter - Connects Model and View
"""
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from typing import Dict, Any
from model.smu_model import SMUModel
from view.view import View
from view.components.config_dialog import ConfigDialog


class MainPresenter:
    """Presenter class that connects Model and View"""
    
    def __init__(self):
        """Initialize the presenter"""
        # Initialize closing flag first to prevent AttributeError
        self.closing = False
        
        # Create model and view
        self.model = SMUModel()
        self.view = View()
        
        # Initialize settings and timer
        self.setting_window = qtc.QSettings('KeithleyIV_RT', 'windows size')
        self.timer = qtc.QTimer()
        self.timer.timeout.connect(self.timeOutEvent)
        
        # Setup
        self._setup_view()
        self._connect_signals()
        self._load_initial_data()
        
        # Show view
        self.view.show()
    
    def _setup_view(self):
        """Setup view with initial data"""
        self.view.load_settings(self.setting_window)
    
    def _connect_signals(self):
        """Connect all UI signals"""
        # Button signals
        self.view.start_button.clicked.connect(self.start_clicked)
        self.view.stop_button.clicked.connect(self.stop_clicked)
        self.view.exit_button.clicked.connect(self.exit_clicked)
        self.view.configure_button.clicked.connect(self.open_config_dialog)
        self.view.clear_graph_button.clicked.connect(self.clear_graph_clicked)
        
        # Close signal
        self.view.closeSignal.connect(self.on_view_closed)
    
    def _load_initial_data(self):
        """Load initial data from model"""
        self.model.load_config()
        self._update_view_from_model()
        
        # Initialize state machine
        self.model.state_machine_function()
    
    def _update_view_from_model(self):
        """Update view with current model data"""
        # Update communication text with filepath if available
        if self.model.data.filepath:
            self.view.communication_text.setText(self.model.data.filepath)
    
    def _update_button_states(self, start_enabled: bool = True, stop_enabled: bool = False, exit_enabled: bool = True):
        """Update button states"""
        self.view.start_button.setEnabled(start_enabled)
        self.view.stop_button.setEnabled(stop_enabled)
        self.view.exit_button.setEnabled(exit_enabled)
    
    def show_popup(self, msg: str):
        """Show popup message"""
        qtw.QMessageBox.information(self.view, "Information", msg)
    
    # Event handlers
    def start_clicked(self):
        """Handle start button click"""
        print("start_clicked")
        self.model.set_state(self.model.state['start'])
        self._update_button_states(start_enabled=False, stop_enabled=True, exit_enabled=False)
        self.view.message('start')
        
        # Start timer based on measurement mode
        if self.model.get_config()['global']['meas_mode'] == 'IV':
            timeout = self.model.iv_starter()
            if timeout:
                self.timer_function(timeout)
        elif self.model.get_config()['global']['meas_mode'] == 'RT':
            timeout = self.model.rt_starter()
            if timeout:
                # For RT mode, take first measurement immediately at time 0
                self.rt_get_plot()
                # Then start the timer for subsequent measurements
                self.timer_function(timeout)
    
    def stop_clicked(self):
        """Handle stop button click"""
        # Stop timer
        if self.timer.isActive():
            self.timer.stop()
        
        self.model.set_state(self.model.state['stop'])
        self._update_button_states()
        self.view.message('stop')
    
    def exit_clicked(self):
        """Handle exit button click"""
        # Stop any ongoing measurement first
        if self.model.is_started():
            self.stop_clicked()
        
        # Set exit state
        self.model.set_state(self.model.state['exit'])
        self.view.message('exit')
        
        # Close the application
        self.view.close()
        
    
    def clear_graph_clicked(self):
        """Handle clear graph button click"""
        self.clear_data()
    
    def open_config_dialog(self):
        """Open configuration dialog"""
        dialog = ConfigDialog(self.model.get_config(), parent=self.view)
        if dialog.exec_():
            updated_config = dialog.get_config()
            self.model.update_config(updated_config)
            print("[Presenter] Config updated:", self.model.get_config())
    
    def on_view_closed(self):
        """Handle view close event"""
        # Prevent multiple calls
        if self.closing:
            return
        
        self.closing = True
        self.model.save_config()
        
        # Check if view still exists before trying to access it
        try:
            if hasattr(self, 'view') and self.view is not None:
                self.view.save_settings(self.setting_window)
        except RuntimeError:
            # View has already been deleted, which is normal during close
            print("View already closed, skipping save_settings")
        
        print("MainView closed")
    
    def clear_data(self):
        """Clear all measurement data"""
        self.model.clear_data()
        self.view.clear_plot()
    
    # Timer and measurement methods
    def timer_function(self, time_out: int):
        """Start timer with specified timeout"""
        self.timer.start(int(time_out))
    
    def timeOutEvent(self):
        """Handle timer timeout event"""
        print("go to main_window timeOutEvent")
        if self.model.get_config()['global']['meas_mode'] == 'IV':
            self.iv_get_plot()
        elif self.model.get_config()['global']['meas_mode'] == 'RT':
            self.rt_get_plot()
    
    def iv_get_plot(self):
        """Handle IV measurement plotting"""
        x_vals, y_vals = self.model.iv_get_plot()
        
        # Update view
        self.view.plot_iv(
            x_vals, y_vals, 
            self.model.get_config()['global']['y_scale'],
            self.model.data.x_alldata, 
            self.model.data.y_alldata
        )
        
        # Update communication text
        if self.model.data.filepath:
            self.view.communication_text.setText(self.model.data.filepath)
        
        # Check if measurement is complete
        if self.model.get_current_state() == self.model.state['save_data']:
            # Measurement complete, stop timer and save data
            if self.timer.isActive():
                self.timer.stop()
            self.model.set_state(self.model.state['save_data'])
            self.stop_clicked()
    
    def rt_get_plot(self):
        """Handle RT measurement plotting"""
        x_vals, y_vals = self.model.rt_get_plot()
        
        # Update view
        self.view.plot_rt(
            x_vals, y_vals, 
            self.model.get_config()['global']['y_scale'],
            self.model.data.x_alldata, 
            self.model.data.y_alldata, 
        )
        
        # Update communication text
        if self.model.data.filepath:
            self.view.communication_text.setText(self.model.data.filepath)
    
    # Public interface methods
    def get_model(self) -> SMUModel:
        """Get the model instance"""
        return self.model
    
    def get_view(self) -> View:
        """Get the view instance"""
        return self.view
    
    def close(self):
        """Close the application"""
        if self.model.is_started():
            self.stop_clicked()
        self.view.close() 