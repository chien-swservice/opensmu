"""Tests for MVP architecture — model and component imports."""
import pytest
from model.smu_model import SMUModel, SMUState
from model.measurement_data import MeasurementData


def test_model_imports():
    from model.smu_model import SMUModel
    from model.measurement_data import MeasurementData
    from devices.smu_simulation import SMUSimulation
    from devices.smu_base import SMUBase


def test_model_creates_with_defaults():
    model = SMUModel()
    assert model.get_config() is not None
    assert model.get_measurement_data() is not None
    assert model.is_started() is False


def test_model_default_config_keys():
    model = SMUModel()
    config = model.get_config()
    assert 'IV' in config
    assert 'RT' in config
    assert 'global' in config


def test_model_default_smu_type_is_simulation():
    model = SMUModel()
    from devices.smu_simulation import SMUSimulation
    assert isinstance(model.SMU, SMUSimulation)


def test_model_initial_state_is_initialize():
    model = SMUModel()
    assert model.currState == SMUState.INITIALIZE


def test_presenter_can_be_imported():
    pytest.importorskip("PyQt5", reason="PyQt5 not installed")
    from presenter.main_presenter import MainPresenter
