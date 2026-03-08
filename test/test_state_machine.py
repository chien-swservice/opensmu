"""Integration tests for the SMUModel hierarchical state machine."""
import pytest
from model.smu_model import SMUModel


@pytest.fixture
def model():
    return SMUModel()


def test_initial_state_is_initialize(model):
    assert model.currState == model.state['initialize']


def test_initializer_transitions_to_wait(model):
    model.initializer()
    assert model.currState == model.state['wait_for_event']


def test_state_machine_function_runs_initialize(model):
    model.state_machine_function()
    assert model.currState == model.state['wait_for_event']


def test_waiter_does_nothing(model):
    model.currState = model.state['wait_for_event']
    model.waiter()  # should not raise
    assert model.currState == model.state['wait_for_event']


def test_starter_sets_started_flag(model):
    model.currState = model.state['start']
    model.starter()
    assert model.started is True


def test_starter_with_simulation_succeeds(model):
    model.currState = model.state['start']
    model.starter()
    # Simulation always connects successfully
    assert model.started is True


def test_stoper_clears_started_flag(model):
    # Put model in a started state first
    model.currState = model.state['start']
    model.starter()
    assert model.started is True

    model.currState = model.state['stop']
    model.stoper()
    assert model.started is False


def test_stoper_transitions_to_wait(model):
    model.currState = model.state['start']
    model.starter()
    model.stoper()
    assert model.currState == model.state['wait_for_event']


def test_exiter_when_not_started(model):
    model.currState = model.state['exit']
    model.exiter()
    # When not started, stays in exit state (presenter handles shutdown)
    assert model.currState == model.state['exit']


def test_exiter_when_started_transitions_to_stop(model):
    model.currState = model.state['start']
    model.starter()
    model.currState = model.state['exit']
    model.exiter()
    assert model.currState == model.state['stop']


def test_saver_transitions_to_stop(model):
    model.currState = model.state['save_data']
    model.saver()
    assert model.currState == model.state['stop']


def test_default_handler_does_not_raise(model):
    model.default()  # unknown state, should not raise


def test_switch_unknown_state_calls_default(model):
    model.switch(999)  # should not raise


def test_set_state_triggers_state_machine(model):
    model.set_state(model.state['initialize'])
    assert model.currState == model.state['wait_for_event']


def test_repeat_increments_on_stop(model):
    model.currState = model.state['start']
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
