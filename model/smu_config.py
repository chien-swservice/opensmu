"""SMU configuration management — load, save, defaults, device factory."""
import json
from pathlib import Path
from typing import Dict, Any, List
import pyvisa

from devices.smu_simulation import SMUSimulation
from devices.keithley2450 import keithley_2450
from devices.keithley2611 import keithley_2611
from devices.keithley26xxab import keithley_26xxab
from devices.keithley24xx import keithley_24xx
from devices.keysightB2900 import keysight_b2900


class SMUConfigMixin:
    """Mixin providing configuration management and SMU device factory."""

    def _init_default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            'IV': {
                'source_delay_ms': 50,
                'voltage_range': 2.0,
                'startV': -1.0,
                'stopV': 1.0,
                'stepV': 0.1,
                'current_range': 1e-6,
            },
            'RT': {
                'rt_voltage_range': 2.0,
                'rt_voltage_set': 0.5,
                'rt_current_range': 1e-6,
                'rt_aperture': 1.0,
            },
            'global': {
                'smu_type': 'simulation',
                'visa_name': 'GPIB1::1::INSTR',
                'terminal': 'FRONT',
                'nplc': 1.0,
                'meas_mode': 'IV',
                'save_folder': str(Path.home() / 'opensmu_data'),
                'file_name': 'data',
                'y_scale': 'linear',
            },
        }

    def _create_smu_instance(self):
        """Instantiate the correct SMU driver based on config."""
        smu_type = self.config['global'].get('smu_type', 'simulation')
        drivers = {
            'keithley2450': keithley_2450,
            'keithley2611': keithley_2611,
            'keithley26xxab': keithley_26xxab,
            'keithley24xx': keithley_24xx,
            'agilent_b2900': keysight_b2900,
        }
        return drivers.get(smu_type, SMUSimulation)()

    def load_config(self) -> bool:
        """Load configuration from config/config.json."""
        try:
            with open('config/config.json', 'r') as f:
                self.config = json.load(f)
            print("Configuration loaded from config/config.json")
            self.SMU = self._create_smu_instance()
            return True
        except FileNotFoundError:
            print("config/config.json not found. Using default configuration.")
            return False
        except json.JSONDecodeError:
            print("Error decoding config/config.json. Using default configuration.")
            return False

    def save_config(self) -> bool:
        """Save current configuration to config/config.json."""
        try:
            with open('config/config.json', 'w') as f:
                json.dump(self.config, f, indent=4)
            print("Configuration saved to config/config.json")
            return True
        except Exception as e:
            print(f"Error saving config/config.json: {e}")
            return False

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Apply new configuration and recreate SMU instance if type changed."""
        old_smu_type = self.config['global'].get('smu_type', 'simulation')

        self.config['IV'].update(new_config['IV'])
        self.config['RT'].update(new_config['RT'])
        self.config['global'].update(new_config['global'])

        new_smu_type = self.config['global'].get('smu_type', 'simulation')
        if old_smu_type != new_smu_type:
            self.SMU = self._create_smu_instance()
            print(f"SMU type changed from {old_smu_type} to {new_smu_type}")

        self.save_config()

    def get_config(self) -> Dict[str, Any]:
        """Return current configuration."""
        return self.config

    def list_available_devices(self) -> List[str]:
        """List all available VISA resources."""
        try:
            rm = pyvisa.ResourceManager()
            resources = rm.list_resources()
            print(f"🔍 Found {len(resources)} VISA resources:")
            for i, resource in enumerate(resources):
                print(f"   {i+1}. {resource}")
            return resources
        except Exception as e:
            print(f"❌ Error listing VISA resources: {e}")
            return []
