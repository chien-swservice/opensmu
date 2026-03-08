"""Unit tests for MeasurementData dataclass."""
import pytest
from model.measurement_data import MeasurementData


@pytest.fixture
def data():
    return MeasurementData()


def test_initial_x_vals_empty(data):
    assert data.x_vals == []


def test_initial_y_vals_empty(data):
    assert data.y_vals == []


def test_initial_repeat_zero(data):
    assert data.repeat == 0


def test_initial_index_zero(data):
    assert data.index == 0


def test_initial_list_v_empty(data):
    assert data.listV == []


def test_clear_current_data(data):
    data.x_vals.extend([1.0, 2.0])
    data.y_vals.extend([0.001, 0.002])
    data.logy_curr_data.extend([1e-3, 2e-3])
    data.clear_current_data()
    assert data.x_vals == []
    assert data.y_vals == []
    assert data.logy_curr_data == []


def test_clear_all_data(data):
    data.x_vals.extend([1.0, 2.0])
    data.y_vals.extend([0.001, 0.002])
    data.x_alldata.append([1.0, 2.0])
    data.y_alldata.append([0.001, 0.002])
    data.logy_all_data.append([1e-3, 2e-3])
    data.clear_all_data()
    assert data.x_vals == []
    assert data.y_vals == []
    assert data.x_alldata == []
    assert data.y_alldata == []
    assert data.logy_all_data == []


def test_save_current_data_appends_to_history(data):
    data.x_vals.extend([1.0, 2.0])
    data.y_vals.extend([0.001, 0.002])
    data.logy_curr_data.extend([1e-3, 2e-3])
    data.save_current_data()
    assert len(data.x_alldata) == 1
    assert data.x_alldata[0] == [1.0, 2.0]
    assert data.y_alldata[0] == [0.001, 0.002]


def test_save_current_data_copies_not_references(data):
    data.x_vals.extend([1.0, 2.0])
    data.y_vals.extend([0.001, 0.002])
    data.logy_curr_data.extend([1e-3])
    data.save_current_data()
    data.x_vals.clear()
    # Historical data should be unaffected
    assert data.x_alldata[0] == [1.0, 2.0]


def test_save_current_data_multiple_runs(data):
    for i in range(3):
        data.x_vals.clear()
        data.y_vals.clear()
        data.logy_curr_data.clear()
        data.x_vals.append(float(i))
        data.y_vals.append(float(i) * 1e-3)
        data.logy_curr_data.append(float(i) * 1e-3)
        data.save_current_data()
    assert len(data.x_alldata) == 3


def test_reset_for_new_measurement_clears_current(data):
    data.x_vals.extend([1.0, 2.0])
    data.y_vals.extend([0.001, 0.002])
    data.index = 5
    data.reset_for_new_measurement()
    assert data.x_vals == []
    assert data.y_vals == []
    assert data.index == 0


def test_reset_for_new_measurement_preserves_history(data):
    data.x_alldata.append([1.0])
    data.y_alldata.append([0.001])
    data.reset_for_new_measurement()
    assert len(data.x_alldata) == 1
