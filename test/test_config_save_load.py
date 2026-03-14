"""Tests for configuration save and load functionality."""
import json
import os
import tempfile
import pytest
from model.smu_model import SMUModel


def test_default_config_has_required_sections():
    model = SMUModel()
    config = model.get_config()
    assert 'IV' in config
    assert 'RT' in config
    assert 'global' in config


def test_default_iv_config_keys():
    model = SMUModel()
    iv = model.get_config()['IV']
    assert 'source_delay_ms' in iv
    assert 'voltage_range' in iv
    assert 'startV' in iv
    assert 'stopV' in iv
    assert 'stepV' in iv
    assert 'current_range' in iv


def test_default_rt_config_keys():
    model = SMUModel()
    rt = model.get_config()['RT']
    assert 'rt_voltage_range' in rt
    assert 'rt_voltage_set' in rt
    assert 'rt_current_range' in rt
    assert 'rt_aperture' in rt


def test_default_global_config_keys():
    model = SMUModel()
    g = model.get_config()['global']
    assert 'smu_type' in g
    assert 'visa_name' in g
    assert 'terminal' in g
    assert 'nplc' in g
    assert 'meas_mode' in g
    assert 'save_folder' in g
    assert 'file_name' in g
    assert 'y_scale' in g


def test_save_and_load_roundtrip(tmp_path):
    config_file = tmp_path / 'config.json'
    config = {
        'IV': {'source_delay_ms': 100, 'voltage_range': 5.0,
               'startV': -2.0, 'stopV': 2.0, 'stepV': 0.1, 'current_range': 1e-6},
        'RT': {'rt_voltage_range': 2.0, 'rt_voltage_set': 0.5,
               'rt_current_range': 1e-6, 'rt_aperture': 1.0},
        'global': {'smu_type': 'simulation', 'visa_name': 'GPIB0::1::INSTR',
                   'terminal': 'FRONT', 'nplc': 1.0, 'meas_mode': 'IV',
                   'save_folder': str(tmp_path), 'file_name': 'test', 'y_scale': 'linear'}
    }
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)

    with open(config_file, 'r') as f:
        loaded = json.load(f)

    assert loaded['IV']['source_delay_ms'] == 100
    assert loaded['global']['smu_type'] == 'simulation'


def test_load_missing_file_returns_false(tmp_path, monkeypatch):
    import model.smu_config as smu_config
    monkeypatch.setattr(smu_config, 'CONFIG_PATH', tmp_path / 'nonexistent.json')
    model = SMUModel()
    result = model.load_config()
    assert result is False


def test_update_config_persists_values():
    model = SMUModel()
    new_config = {
        'IV': {**model.get_config()['IV'], 'startV': -5.0},
        'RT': model.get_config()['RT'],
        'global': model.get_config()['global'],
    }
    model.config.update(new_config)
    assert model.get_config()['IV']['startV'] == -5.0


def test_save_folder_is_cross_platform_path():
    model = SMUModel()
    save_folder = model.get_config()['global']['save_folder']
    # Must be an absolute path (cross-platform)
    assert os.path.isabs(save_folder)
