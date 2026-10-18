from Engineering.beam_analysis import calculate_beam_udl
from Engineering.design_checks import check_value
from Engineering.supports import SupportCondition


def _validate_section(section):
    """
    Validate that the supplied section provides the geometric
    properties required by the panel analysis.

    Supported section objects include:

    - RectangularSection
    - ManufacturerProfile
    """

    if section is None:
        raise TypeError(
            "section must be a valid section object."
        )

    if not hasattr(section, "area"):
        raise TypeError(
            "section must provide an 'area' property."
        )

    if not hasattr(section, "second_moment_of_area"):
        raise TypeError(
            "section must provide a 'second_moment_of_area' "
            "property."
        )

    if section.area <= 0:
        raise ValueError(
            "section area must be greater than zero."
        )

    if section.second_moment_of_area <= 0:
        raise ValueError(
            "section second moment of area must be greater "
            "than zero."
        )


def _get_section_modulus(section):
    """
    Return the bending section modulus about the x-axis.

    The section object may expose this as either:

    - section_modulus
    - section_modulus_x

    No section modulus is invented for arbitrary manufacturer
    profiles if it is not available.
    """

    section_modulus = getattr(
        section,
        "section_modulus",
        None,
    )

    if section_modulus is not None:
        return section_modulus

    section_modulus = getattr(
        section,
        "section_modulus_x",
        None,
    )

    return section_modulus


def calculate_panel_udl(
    span,
    tributary_width,
    section,
    area_load,
    material,
    support_condition=SupportCondition.SIMPLY_SUPPORTED,
    shear_correction_factor=5 / 6,
):
    """
    Calculate the response of a panel strip subjected to a
    uniformly distributed area load.

    The panel is represented as a beam strip.

    Area load:

        N/m²

    is converted to line load:

        w = q * tributary_width

    Supported section objects include rectangular sections
    and manufacturer catalogue profiles.
    """

    if span <= 0:
        raise ValueError(
            "span must be greater than zero."
        )

    if tributary_width <= 0:
        raise ValueError(
            "tributary_width must be greater than zero."
        )

    if area_load < 0:
        raise ValueError(
            "area_load cannot be negative."
        )

    _validate_section(section)

    distributed_load = (
        area_load
        * tributary_width
    )

    results = calculate_beam_udl(
        span=span,
        distributed_load=distributed_load,
        material=material,
        section=section,
        support_condition=support_condition,
        shear_correction_factor=shear_correction_factor,
    )

    return results


def check_panel_design(
    span,
    tributary_width,
    section,
    area_load,
    material,
    allowable_stress,
    allowable_deflection,
    support_condition=SupportCondition.SIMPLY_SUPPORTED,
    shear_correction_factor=5 / 6,
):
    """
    Perform structural analysis and design checks for a panel strip.

    The panel is represented as a beam subjected to a uniformly
    distributed line load obtained from the supplied area load.

    Two checks are performed:

    1. Bending stress
    2. Maximum deflection
    """

    if allowable_stress <= 0:
        raise ValueError(
            "allowable_stress must be greater than zero."
        )

    if allowable_deflection <= 0:
        raise ValueError(
            "allowable_deflection must be greater than zero."
        )

    _validate_section(section)

    # --------------------------------------------------------
    # STRUCTURAL ANALYSIS
    # --------------------------------------------------------

    results = calculate_panel_udl(
        span=span,
        tributary_width=tributary_width,
        section=section,
        area_load=area_load,
        material=material,
        support_condition=support_condition,
        shear_correction_factor=shear_correction_factor,
    )

    # --------------------------------------------------------
    # SECTION MODULUS
    # --------------------------------------------------------

    section_modulus = _get_section_modulus(section)

    if section_modulus is None:

        raise ValueError(
            "The selected section does not have a section "
            "modulus (Zxx) available. Bending stress cannot "
            "currently be checked for this profile."
        )

    if section_modulus <= 0:

        raise ValueError(
            "Section modulus must be greater than zero."
        )

    # --------------------------------------------------------
    # BENDING STRESS
    # --------------------------------------------------------

    bending_stress = (
        results.max_bending_moment
        / section_modulus
    )

    # Keep result object consistent with the calculated
    # section properties.
    results.bending_stress = bending_stress
    results.section_modulus = section_modulus

    # --------------------------------------------------------
    # STRESS CHECK
    # --------------------------------------------------------

    stress_check = check_value(
        calculated_value=bending_stress,
        allowable_value=allowable_stress,
    )

    # --------------------------------------------------------
    # DEFLECTION CHECK
    # --------------------------------------------------------

    deflection_check = check_value(
        calculated_value=results.max_deflection,
        allowable_value=allowable_deflection,
    )

    # --------------------------------------------------------
    # OVERALL RESULT
    # --------------------------------------------------------

    overall_pass = (
        stress_check.passes
        and deflection_check.passes
    )

    return {
        "panel_results": results,
        "stress_check": stress_check,
        "deflection_check": deflection_check,
        "overall_pass": overall_pass,
    }