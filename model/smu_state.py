"""SMU state machine states."""
from enum import Enum, auto


class SMUState(Enum):
    """States for the SMU hierarchical state machine."""
    INITIALIZE = auto()
    WAIT_FOR_EVENT = auto()
    START = auto()
    STOP = auto()
    EXIT = auto()
    SAVE_DATA = auto()
