import pytest

from Engineering.load_cases import (
    calculate_self_weight_line_load,
    calculate_load_cases,
)


class DummySection:
    def __init__(
        self,
        mass_per_length=None,
        area=None,
    ):
        self.mass_per_length = mass_per_length
        self.area = area


class DummyMaterialRecord:
    def __init__(self, density=None):
        self.density = density


def test_self_weight_from_manufacturer_mass():

    section = DummySection(
        mass_per_length=5.0
    )

    weight = calculate_self_weight_line_load(
        section
    )

    assert weight == pytest.approx(
        5.0 * 9.81
    )


def test_self_weight_from_density_and_area():

    section = DummySection(
        mass_per_length=None,
        area=0.001,
    )

    material = DummyMaterialRecord(
        density=1720.0
    )

    weight = calculate_self_weight_line_load(
        section,
        material,
    )

    assert weight == pytest.approx(
        1720.0 * 0.001 * 9.81
    )


def test_self_weight_zero_when_no_data():

    section = DummySection()

    weight = calculate_self_weight_line_load(
        section
    )

    assert weight == 0.0


def test_sls_load_combination():

    results = calculate_load_cases(
        span=4.0,
        tributary_width=1.0,
        self_weight_line_load=50.0,
        permanent_area_load=500.0,
        variable_area_load=2000.0,
    )

    sls = results["SLS"]

    assert sls.permanent_line_load == pytest.approx(
        550.0
    )

    assert sls.variable_line_load == pytest.approx(
        2000.0
    )

    assert sls.total_line_load == pytest.approx(
        2550.0
    )

    assert sls.total_load == pytest.approx(
        2550.0 * 4.0
    )


def test_uls_load_combination():

    results = calculate_load_cases(
        span=4.0,
        tributary_width=1.0,
        self_weight_line_load=50.0,
        permanent_area_load=500.0,
        variable_area_load=2000.0,
        gamma_g=1.35,
        gamma_q=1.50,
    )

    uls = results["ULS"]

    expected = (
        1.35 * 550.0
        + 1.50 * 2000.0
    )

    assert uls.total_line_load == pytest.approx(
        expected
    )


def test_invalid_span():

    with pytest.raises(ValueError):

        calculate_load_cases(
            span=0,
            tributary_width=1.0,
            self_weight_line_load=50.0,
            permanent_area_load=500.0,
            variable_area_load=2000.0,
        )


def test_invalid_tributary_width():

    with pytest.raises(ValueError):

        calculate_load_cases(
            span=4.0,
            tributary_width=0,
            self_weight_line_load=50.0,
            permanent_area_load=500.0,
            variable_area_load=2000.0,
        )


def test_invalid_load():

    with pytest.raises(ValueError):

        calculate_load_cases(
            span=4.0,
            tributary_width=1.0,
            self_weight_line_load=-1.0,
            permanent_area_load=500.0,
            variable_area_load=2000.0,
        )