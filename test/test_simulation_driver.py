"""Unit tests for SMUSimulation driver."""
import pytest
from devices.smu_simulation import SMUSimulation


@pytest.fixture
def smu():
    return SMUSimulation()


def test_initial_state(smu):
    assert smu.connected is False
    assert smu.voltage == 0.0
    assert smu.output_on is False


def test_connect(smu):
    smu.create_smu_connector('SIM::0')
    assert smu.connected is True


def test_identify_returns_string(smu):
    result = smu.identify_smu()
    assert isinstance(result, str)
    assert len(result) > 0


def test_set_voltage_level(smu):
    smu.create_smu_connector('SIM::0')
    smu.set_voltage_level(1.5)
    assert smu.voltage == pytest.approx(1.5)


def test_set_voltage_level_from_string(smu):
    smu.create_smu_connector('SIM::0')
    smu.set_voltage_level('2.0')
    assert smu.voltage == pytest.approx(2.0)


def test_readout_returns_zero_when_output_off(smu):
    smu.create_smu_connector('SIM::0')
    smu.set_voltage_level(1.0)
    assert smu.output_on is False
    assert smu.readout() == 0.0


def test_readout_returns_current_when_output_on(smu):
    smu.create_smu_connector('SIM::0')
    smu.set_voltage_level(1.0)
    smu.set_output_on()
    current = smu.readout()
    # I = V/R + noise, R=1k => ~1mA ± 1µA
    assert abs(current - 1e-3) < 10e-6


def test_readout_scales_with_voltage(smu):
    smu.create_smu_connector('SIM::0')
    smu.set_output_on()

    smu.set_voltage_level(0.5)
    i_half = smu.readout()

    smu.set_voltage_level(1.0)
    i_full = smu.readout()

    # Higher voltage → higher current
    assert i_full > i_half


def test_output_on_off(smu):
    smu.set_output_on()
    assert smu.output_on is True
    smu.set_output_off()
    assert smu.output_on is False


def test_reset_clears_voltage_and_output(smu):
    smu.create_smu_connector('SIM::0')
    smu.set_voltage_level(5.0)
    smu.set_output_on()
    smu.reset_smu()
    assert smu.voltage == 0.0
    assert smu.output_on is False


def test_close_disconnects(smu):
    smu.create_smu_connector('SIM::0')
    assert smu.connected is True
    smu.close_smu()
    assert smu.connected is False


def test_all_abstract_methods_implemented(smu):
    """Ensure no NotImplementedError is raised for any base method."""
    smu.create_smu_connector('SIM::0')
    smu.reset_smu()
    smu.identify_smu()
    smu.query_smu('*IDN?')
    smu.write_smu('*RST')
    smu.read_smu()
    smu.timeout_smu(10000)
    smu.set_front_terminal()
    smu.set_rear_terminal()
    smu.set_source_voltage_delay_auto_on()
    smu.set_source_voltage_delay_auto_off()
    smu.set_source_voltage_delay_time(50)
    smu.set_source_function_voltage()
    smu.set_source_function_current()
    smu.set_voltage_range_auto_on()
    smu.set_voltage_range_auto_off()
    smu.set_voltage_range_value(2.0)
    smu.set_voltage_level(1.0)
    smu.set_measure_mode_current()
    smu.set_measure_current_range(1e-6)
    smu.set_measure_current_limit(1e-6)
    smu.set_measure_current_nplc(1.0)
    smu.set_output_on()
    smu.readout()
    smu.set_output_off()
    smu.close_smu()
