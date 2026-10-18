import pytest

from Engineering.panel_analysis import (
    calculate_panel_udl,
    check_panel_design
)
from Engineering.supports import SupportCondition
from Engineering.material import Material
from Engineering.profiles import rectangular_panel_section


def test_panel_area_load_conversion():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    assert results.distributed_load == pytest.approx(1000.0)


def test_panel_total_load():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    assert results.total_load == pytest.approx(2000.0)


def test_panel_reactions():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    assert results.left_reaction == pytest.approx(1000.0)
    assert results.right_reaction == pytest.approx(1000.0)


def test_panel_maximum_bending_moment():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    assert results.max_bending_moment == pytest.approx(500.0)


def test_panel_section_properties():
    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    assert section.area == pytest.approx(0.005)

    expected_I = 0.5 * 0.01**3 / 12
    assert section.second_moment_of_area == pytest.approx(expected_I)

    expected_Z = expected_I / (0.01 / 2)
    assert section.section_modulus == pytest.approx(expected_Z)


def test_panel_bending_stress():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    expected_stress = (
        results.max_bending_moment
        / results.section_modulus
    )

    assert results.bending_stress == pytest.approx(
        expected_stress
    )


def test_panel_bending_deflection():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    assert results.bending_deflection > 0


def test_panel_zero_shear_without_shear_modulus():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    assert results.shear_deflection == pytest.approx(0.0)
    assert results.max_deflection == pytest.approx(
        results.bending_deflection
    )
    assert results.shear_contribution == pytest.approx(0.0)


def test_panel_shear_deflection_with_test_shear_modulus():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=3e9,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    assert results.shear_deflection > 0
    assert results.max_deflection == pytest.approx(
        results.bending_deflection
        + results.shear_deflection
    )


def test_panel_shear_contribution():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=3e9,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    assert results.shear_contribution > 0
    assert results.shear_contribution < 100


def test_panel_diagram_arrays():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    assert len(results.x) > 0
    assert len(results.shear) == len(results.x)
    assert len(results.moment) == len(results.x)
    assert len(results.deflection) == len(results.x)


def test_panel_diagram_endpoints():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material
    )

    assert results.x[0] == pytest.approx(0.0)
    assert results.x[-1] == pytest.approx(2.0)


def test_panel_simply_supported_symmetry():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material,
        support_condition=SupportCondition.SIMPLY_SUPPORTED
    )

    assert results.left_reaction == pytest.approx(
        results.right_reaction
    )


def test_panel_fixed_fixed_moment():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material,
        support_condition=SupportCondition.FIXED_FIXED
    )

    assert results.max_bending_moment > 0


def test_panel_fixed_fixed_zero_shear_contribution_without_G():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    results = calculate_panel_udl(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material,
        support_condition=SupportCondition.FIXED_FIXED
    )

    assert results.shear_deflection == pytest.approx(0.0)
    assert results.shear_contribution == pytest.approx(0.0)


def test_panel_invalid_span():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    with pytest.raises(ValueError):
        calculate_panel_udl(
            span=0,
            tributary_width=0.5,
            section=section,
            area_load=2000,
            material=material
        )


def test_panel_invalid_tributary_width():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    with pytest.raises(ValueError):
        calculate_panel_udl(
            span=2.0,
            tributary_width=0,
            section=section,
            area_load=2000,
            material=material
        )


def test_panel_invalid_area_load():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    with pytest.raises(ValueError):
        calculate_panel_udl(
            span=2.0,
            tributary_width=0.5,
            section=section,
            area_load=-1,
            material=material
        )


def test_panel_invalid_section_type():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    with pytest.raises(TypeError):
        calculate_panel_udl(
            span=2.0,
            tributary_width=0.5,
            section_width=0.5,
            thickness=0.01,
            area_load=2000,
            material=material
        )


def test_panel_design_check_structure():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    result = check_panel_design(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material,
        allowable_stress=240e6,
        allowable_deflection=0.3
    )

    assert "panel_results" in result
    assert "stress_check" in result
    assert "deflection_check" in result
    assert "overall_pass" in result


def test_panel_design_passes():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    result = check_panel_design(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material,
        allowable_stress=240e6,
        allowable_deflection=0.3
    )

    assert result["overall_pass"] is True


def test_panel_design_fails_stress_check():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=1e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    result = check_panel_design(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material,
        allowable_stress=1e6,
        allowable_deflection=0.3
    )

    assert result["overall_pass"] is False


def test_panel_design_fails_deflection_check():
    material = Material(
        name="Test material",
        youngs_modulus=23e9,
        transverse_youngs_modulus=7e9,
        shear_modulus=None,
        allowable_stress=240e6
    )

    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    result = check_panel_design(
        span=2.0,
        tributary_width=0.5,
        section=section,
        area_load=2000,
        material=material,
        allowable_stress=240e6,
        allowable_deflection=0.0001
    )

    assert result["overall_pass"] is False