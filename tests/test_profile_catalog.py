import pytest

from Engineering.profiles import (
    RectangularSection,
    rectangular_panel_section,
    evergrip_profile_catalog,
)


def test_rectangular_panel_section_properties():
    section = rectangular_panel_section(
        width=0.5,
        thickness=0.01
    )

    assert isinstance(section, RectangularSection)

    assert section.area == pytest.approx(0.005)

    assert section.second_moment_of_area == pytest.approx(
        0.5 * 0.01**3 / 12
    )

    assert section.section_modulus == pytest.approx(
        (0.5 * 0.01**3 / 12) / (0.01 / 2)
    )


def test_evergrip_profile_catalog_not_empty():

    profiles = evergrip_profile_catalog()

    assert len(profiles) > 0


def test_evergrip_profile_catalog_contains_expected_types():

    profiles = evergrip_profile_catalog()

    section_types = {
        profile.section_type
        for profile in profiles
    }

    assert "Angle" in section_types
    assert "Square tube" in section_types
    assert "Channel" in section_types
    assert "I beam" in section_types
    assert "Round tube" in section_types
    assert "Plate" in section_types


def test_evergrip_profile_catalog_contains_known_square_tube():

    profiles = evergrip_profile_catalog()

    profile = next(
        profile
        for profile in profiles
        if profile.designation == "100 x 100 x 8 mm"
    )

    assert profile.cross_sectional_area == pytest.approx(
        2950e-6
    )

    assert profile.mass_per_length == pytest.approx(
        5.49
    )

    assert profile.second_moment_x == pytest.approx(
        4192000e-12
    )

    assert profile.second_moment_y == pytest.approx(
        4192000e-12
    )


def test_evergrip_profile_catalog_contains_known_i_beam():

    profiles = evergrip_profile_catalog()

    profile = next(
        profile
        for profile in profiles
        if profile.designation == "75 x 150 x 8 x 8 mm"
    )

    assert profile.cross_sectional_area == pytest.approx(
        2292e-6
    )

    assert profile.mass_per_length == pytest.approx(
        4.24
    )

    assert profile.second_moment_x == pytest.approx(
        7745000e-12
    )

    assert profile.second_moment_y == pytest.approx(
        566000e-12
    )


def test_profile_catalog_values_are_positive():

    profiles = evergrip_profile_catalog()

    for profile in profiles:

        assert profile.mass_per_length > 0
        assert profile.cross_sectional_area > 0
        assert profile.second_moment_x > 0

        if profile.second_moment_y is not None:
            assert profile.second_moment_y > 0


def test_profile_catalog_traceability():

    profiles = evergrip_profile_catalog()

    for profile in profiles:

        assert profile.manufacturer == "Evergrip Limited"
        assert "Evergrip" in profile.source
        assert profile.validation_status != ""


def test_profile_self_weight():

    profiles = evergrip_profile_catalog()

    profile = next(
        profile
        for profile in profiles
        if profile.designation == "100 x 100 x 8 mm"
    )

    assert profile.get_self_weight() == pytest.approx(
        5.49 * 9.81
    )


def test_catalogue_profile_has_no_unvalidated_section_modulus():

    profiles = evergrip_profile_catalog()

    for profile in profiles:

        assert profile.section_modulus_x is None