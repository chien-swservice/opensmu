"""
SMU Model — state machine and top-level orchestration.

Business logic is split across three modules:
  - smu_state.py       : SMUState enum
  - smu_config.py      : SMUConfigMixin  (config load/save, device factory)
  - smu_measurement.py : SMUMeasurementMixin (IV, RT, SMU setup)
"""
from .smu_state import SMUState  # re-exported for external imports
from .smu_config import SMUConfigMixin
from .smu_measurement import SMUMeasurementMixin
from .measurement_data import MeasurementData


class SMUModel(SMUConfigMixin, SMUMeasurementMixin):
    """Top-level model: owns the state machine and delegates to mixins."""

    def __init__(self):
        self.config = self._init_default_config()
        self.data = MeasurementData()
        self.SMU = self._create_smu_instance()
        self.started = False
        self.last_meas_mode = self.config['global']['meas_mode']

        self.currState = SMUState.INITIALIZE
        self.switcher = {
            SMUState.INITIALIZE:     self.initializer,
            SMUState.WAIT_FOR_EVENT: self.waiter,
            SMUState.START:          self.starter,
            SMUState.STOP:           self.stoper,
            SMUState.EXIT:           self.exiter,
            SMUState.SAVE_DATA:      self.saver,
        }

    # --- State machine ---

    def switch(self, currentState: SMUState) -> None:
        self.switcher.get(currentState, self.default)()

    def state_machine_function(self) -> None:
        self.switch(self.currState)

    def initializer(self) -> None:
        self.currState = SMUState.WAIT_FOR_EVENT

    def waiter(self) -> None:
        pass

    def starter(self) -> None:
        self.started = True
        self.data.index = 0
        print('Started measurement')

        if self.last_meas_mode != self.config['global']['meas_mode']:
            self.data.clear_all_data()
        self.last_meas_mode = self.config['global']['meas_mode']

        if not self._setup_smu_connection():
            return
        self._configure_smu_basic()

    def stoper(self) -> None:
        print('stop')
        if self.data.file_handle and not self.data.file_handle.closed:
            self.data.file_handle.close()

        self.SMU.reset_smu()
        self.SMU.set_output_off()
        self.SMU.close_smu()
        self.started = False
        self.data.repeat += 1
        self.data.save_current_data()
        self.currState = SMUState.WAIT_FOR_EVENT

    def exiter(self) -> None:
        print('exit')
        if self.started:
            self.currState = SMUState.STOP

    def saver(self) -> None:
        if self.data.file_handle and not self.data.file_handle.closed:
            self.data.file_handle.close()
        self.currState = SMUState.STOP

    def default(self) -> None:
        print("Unknown state")

    # --- Public interface ---

    def get_measurement_data(self) -> MeasurementData:
        return self.data

    def is_started(self) -> bool:
        return self.started

    def get_current_state(self) -> SMUState:
        return self.currState

    def set_state(self, state: SMUState) -> None:
        self.currState = state
        self.state_machine_function()

    def clear_data(self) -> None:
        self.data.clear_all_data()
        self.last_meas_mode = None
