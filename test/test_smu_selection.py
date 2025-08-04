#!/usr/bin/env python3
"""
Test script to verify SMU type selection functionality
"""

from model.smu_model import SMUModel
from devices.smu_simulation import SMUSimulation
from devices.keithley2450 import keithley_2450

def test_smu_creation():
    """Test that different SMU types can be created correctly"""
    
    # Test with simulation SMU
    model = SMUModel()
    model.config['global']['smu_type'] = 'simulation'
    smu = model._create_smu_instance()
    print(f"Created SMU type: {type(smu).__name__}")
    assert isinstance(smu, SMUSimulation), "Should create SMUSimulation instance"
    
    # Test with Keithley 2450 SMU
    model.config['global']['smu_type'] = 'keithley2450'
    smu = model._create_smu_instance()
    print(f"Created SMU type: {type(smu).__name__}")
    assert isinstance(smu, keithley_2450), "Should create keithley_2450 instance"
    
    print("✅ SMU type selection test passed!")

def test_config_update():
    """Test that SMU instance is recreated when config changes"""
    
    model = SMUModel()
    print(f"Initial SMU type: {type(model.SMU).__name__}")
    
    # Update config to change SMU type
    new_config = {
        'IV': model.config['IV'],
        'RT': model.config['RT'],
        'global': {
            **model.config['global'],
            'smu_type': 'keithley2450'
        }
    }
    
    model.update_config(new_config)
    print(f"After config update SMU type: {type(model.SMU).__name__}")
    assert isinstance(model.SMU, keithley_2450), "Should recreate SMU instance"
    
    print("✅ Config update test passed!")

if __name__ == "__main__":
    print("Testing SMU type selection functionality...")
    test_smu_creation()
    test_config_update()
    print("All tests passed! 🎉") 