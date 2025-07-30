import os

class test(object):
    def __init__(self):
       self.config = {
            'IV': {
                'startV': -1.0,
                'stopV': 1.0,
                'stepV': 0.1,
                'voltage_range': 2.0,
                'current_range': 1e-6,
                'source_delay_ms': 50,
                'nplc': 1.0
            },
            'RT': {
                'sampling_rate': 1.0,
                'duration': 10.0,
                'trigger_level': 0.5
            },
            'global': {
                'save_folder': os.path.join(os.getcwd(), 'data'),
                'file_name': 'data',
                'y_scale': 'linear',
                'meas_mode': 'IV',
                'visa_name': 'GPIB1::1::INSTR',
                'terminal': 'FRONT'
            }
        }


if __name__ == "__main__":
    test_instance = test()
    print(test_instance.config['global']['file_name']) 