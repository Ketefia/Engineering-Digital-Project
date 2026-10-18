import pytest

from Engineering.beam_analysis import calculate_beam_udl
from Engineering.materials_library import (
    evergrip_e23_reference,
)
from Engineering.profiles import (
    evergrip_profile_catalog,
)


def test_evergrip_square_tube_can_be_used_by_beam_solver():

    material_record = evergrip_e23_reference()
    material = material_record.get_material()

    profiles = evergrip_profile_catalog()

    section = next(
        profile
        for profile in profiles
        if profile.designation == "100 x 100 x 8 mm"
    )

    result = calculate_beam_udl(
        span=2.0,
        distributed_load=1000.0,
        material=material,
        section=section,
    )

    assert result.second_moment_of_area == pytest.approx(
        4192000e-12
    )

    assert result.max_bending_moment == pytest.approx(
        1000.0 * 2.0**2 / 8
    )

    assert result.total_load == pytest.approx(
        2000.0
    )

    assert result.max_deflection > 0