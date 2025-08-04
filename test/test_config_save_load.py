#!/usr/bin/env python3
"""
Test script to demonstrate configuration saving and loading functionality.
This script shows how the configuration is saved and loaded in the SMU application.
"""

import json
import os

def create_sample_config():
    """Create a sample configuration for testing"""
    config = {
        'IV': {
            'source_delay_ms': 50,
            'voltage_range': 2.0,
            'startV': -1.0,
            'stopV': 1.0,
            'stepV': 0.1,
            'current_range': 1e-6                
        },
        'RT': {
            'rt_voltage_range': 2.0,
            'rt_voltage_set': 0.5,
            'rt_current_range': 1e-6,
            'rt_aperture': 1.0
        },
        'global': {
            'visa_name': 'GPIB1::1::INSTR',
            'terminal': 'FRONT',
            'nplc': 1.0,
            'meas_mode': 'IV',
            'save_folder': os.path.join(os.getcwd(), 'data'),
            'file_name': 'data',
            'y_scale': 'linear'              
        }
    }
    return config

def save_config(config, filename='config/config.json'):
    """Save configuration to JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"Configuration saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving configuration: {e}")
        return False

def load_config(filename='config/config.json'):
    """Load configuration from JSON file"""
    try:
        with open(filename, 'r') as f:
            config = json.load(f)
        print(f"Configuration loaded from {filename}")
        return config
    except FileNotFoundError:
        print(f"{filename} not found. Using default configuration.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding {filename}. Using default configuration.")
        return None
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return None

def print_config(config):
    """Print configuration in a readable format"""
    print("\nCurrent Configuration:")
    print("=" * 50)
    for section, settings in config.items():
        print(f"\n{section.upper()} Settings:")
        print("-" * 30)
        for key, value in settings.items():
            print(f"  {key}: {value}")

def main():
    """Main test function"""
    print("SMU Configuration Save/Load Test")
    print("=" * 40)
    
    # Create sample configuration
    config = create_sample_config()
    print_config(config)
    
    # Save configuration
    print("\n" + "=" * 40)
    print("Saving configuration...")
    if save_config(config):
        print("✓ Configuration saved successfully")
    else:
        print("✗ Failed to save configuration")
    
    # Load configuration
    print("\n" + "=" * 40)
    print("Loading configuration...")
    loaded_config = load_config()
    if loaded_config:
        print("✓ Configuration loaded successfully")
        print_config(loaded_config)
    else:
        print("✗ Failed to load configuration")
    
    # Test with non-existent file
    print("\n" + "=" * 40)
    print("Testing with non-existent file...")
    non_existent_config = load_config('non_existent_config.json')
    if non_existent_config is None:
        print("✓ Correctly handled non-existent file")
    
    print("\n" + "=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    main() 