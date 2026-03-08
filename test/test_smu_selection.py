"""Tests for SMU type selection and instance creation."""
import pytest
from model.smu_model import SMUModel
from devices.smu_simulation import SMUSimulation
from devices.keithley2450 import keithley_2450
from devices.keithley24xx import keithley_24xx
from devices.keithley2611 import keithley_2611
from devices.keithley26xxab import keithley_26xxab
from devices.keysightB2900 import keysight_b2900


@pytest.mark.parametrize("smu_type,expected_class", [
    ('simulation', SMUSimulation),
    ('keithley2450', keithley_2450),
    ('keithley24xx', keithley_24xx),
    ('keithley2611', keithley_2611),
    ('keithley26xxab', keithley_26xxab),
    ('agilent_b2900', keysight_b2900),
])
def test_smu_instance_creation(smu_type, expected_class):
    model = SMUModel()
    model.config['global']['smu_type'] = smu_type
    smu = model._create_smu_instance()
    assert isinstance(smu, expected_class)


def test_unknown_smu_type_falls_back_to_simulation():
    model = SMUModel()
    model.config['global']['smu_type'] = 'unknown_device'
    smu = model._create_smu_instance()
    assert isinstance(smu, SMUSimulation)


def test_smu_recreated_on_type_change():
    model = SMUModel()
    assert isinstance(model.SMU, SMUSimulation)

    new_config = {
        'IV': model.config['IV'],
        'RT': model.config['RT'],
        'global': {**model.config['global'], 'smu_type': 'keithley2450'},
    }
    model.update_config(new_config)
    assert isinstance(model.SMU, keithley_2450)


def test_smu_not_recreated_when_type_unchanged():
    model = SMUModel()
    original_smu = model.SMU
    new_config = {
        'IV': model.config['IV'],
        'RT': model.config['RT'],
        'global': {**model.config['global'], 'smu_type': 'simulation'},
    }
    model.update_config(new_config)
    assert model.SMU is original_smu
