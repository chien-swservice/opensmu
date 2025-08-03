"""
Measurement data structures for SMU application
"""
import time
import os
import datetime
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MeasurementData:
    """Data structure for measurement data"""
    # File handling
    filepath: Optional[str] = None
    file_handle: Optional[object] = None
    
    # Time variables
    start_time: float = field(default_factory=time.time)
    current_time: float = field(default_factory=time.time)
    
    # Plot data
    logy_curr_data: List[float] = field(default_factory=list)
    logy_all_data: List[List[float]] = field(default_factory=list)
    x_alldata: List[List[float]] = field(default_factory=list)
    y_alldata: List[List[float]] = field(default_factory=list)
    repeat: int = 0
    
    # Current measurement data
    x_vals: List[float] = field(default_factory=list)
    y_vals: List[float] = field(default_factory=list)
    index: int = 0
    
    # Voltage list for IV measurements
    listV: List[float] = field(default_factory=list)
    currentV: Optional[float] = None
    currentI: Optional[float] = None
    
    # IV measurement parameters
    numberStep: int = 0
    
    def clear_current_data(self):
        """Clear current measurement data"""
        self.x_vals.clear()
        self.y_vals.clear()
        self.logy_curr_data.clear()
    
    def clear_all_data(self):
        """Clear all measurement data"""
        self.x_alldata.clear()
        self.y_alldata.clear()
        self.logy_all_data.clear()
        self.clear_current_data()
    
    def save_current_data(self):
        """Save current data to historical data"""
        self.x_alldata.append(self.x_vals.copy())
        self.y_alldata.append(self.y_vals.copy())
        self.logy_all_data.append(self.logy_curr_data.copy())
    
    def reset_for_new_measurement(self):
        """Reset data for a new measurement run"""
        self.clear_current_data()
        self.index = 0
        self.start_time = time.time() 