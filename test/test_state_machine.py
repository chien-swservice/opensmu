"""Integration tests for the SMUModel hierarchical state machine."""
import pytest
from model.smu_model import SMUModel, SMUState


@pytest.fixture
def model():
    return SMUModel()


def test_initial_state_is_initialize(model):
    assert model.currState == SMUState.INITIALIZE


def test_initializer_transitions_to_wait(model):
    model.initializer()
    assert model.currState == SMUState.WAIT_FOR_EVENT


def test_state_machine_function_runs_initialize(model):
    model.state_machine_function()
    assert model.currState == SMUState.WAIT_FOR_EVENT


def test_waiter_does_nothing(model):
    model.currState = SMUState.WAIT_FOR_EVENT
    model.waiter()  # should not raise
    assert model.currState == SMUState.WAIT_FOR_EVENT


def test_starter_sets_started_flag(model):
    model.currState = SMUState.START
    model.starter()
    assert model.started is True


def test_starter_with_simulation_succeeds(model):
    model.currState = SMUState.START
    model.starter()
    # Simulation always connects successfully
    assert model.started is True


def test_stoper_clears_started_flag(model):
    # Put model in a started state first
    model.currState = SMUState.START
    model.starter()
    assert model.started is True

    model.currState = SMUState.STOP
    model.stoper()
    assert model.started is False


def test_stoper_transitions_to_wait(model):
    model.currState = SMUState.START
    model.starter()
    model.stoper()
    assert model.currState == SMUState.WAIT_FOR_EVENT


def test_exiter_when_not_started(model):
    model.currState = SMUState.EXIT
    model.exiter()
    # When not started, stays in exit state (presenter handles shutdown)
    assert model.currState == SMUState.EXIT


def test_exiter_when_started_transitions_to_stop(model):
    model.currState = SMUState.START
    model.starter()
    model.currState = SMUState.EXIT
    model.exiter()
    assert model.currState == SMUState.STOP


def test_saver_transitions_to_stop(model):
    model.currState = SMUState.SAVE_DATA
    model.saver()
    assert model.currState == SMUState.STOP


def test_default_handler_does_not_raise(model):
    model.default()  # unknown state, should not raise


def test_switch_unknown_state_calls_default(model):
    model.switch(999)  # should not raise


def test_set_state_triggers_state_machine(model):
    model.set_state(SMUState.INITIALIZE)
    assert model.currState == SMUState.WAIT_FOR_EVENT


def test_repeat_increments_on_stop(model):
    model.currState = SMUState.START
    model.starter()
    initial_repeat = model.data.repeat
    model.stoper()
    assert model.data.repeat == initial_repeat + 1


def test_clear_data_resets_measurement(model):
    model.data.x_vals.append(1.0)
    model.data.y_vals.append(0.001)
    model.clear_data()
    assert len(model.data.x_vals) == 0
    assert len(model.data.y_vals) == 0
