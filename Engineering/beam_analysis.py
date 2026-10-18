import numpy as np

from Engineering.results import (
    BeamPointLoadResult,
    BeamUDLResult,
)

from Engineering.supports import SupportCondition

from Engineering.timoshenko import (
    calculate_shear_deflection_udl,
)


def _get_section_property(section, property_name):
    """
    Get a property from a section object.

    Raises a clear error when the property is required but
    unavailable.
    """

    if section is None:
        raise ValueError(
            f"Section property '{property_name}' requires a section."
        )

    value = getattr(section, property_name, None)

    if value is None:
        raise ValueError(
            f"Section property '{property_name}' is not available"
        )

    return value


def _rectangular_section(width, height):
    """
    Create a rectangular section for backwards compatibility
    with the original beam API.

    width  = section width
    height = section depth
    """

    if width <= 0:
        raise ValueError("Width must be positive.")

    if height <= 0:
        raise ValueError("Height must be positive.")

    area = width * height

    second_moment = (
        width * height**3 / 12
    )

    section_modulus = (
        width * height**2 / 6
    )

    class RectangularCompatibilitySection:
        pass

    section = RectangularCompatibilitySection()

    section.area = area

    section.second_moment_of_area = (
        second_moment
    )

    section.section_modulus = (
        section_modulus
    )

    # Temporary rectangular approximation for
    # Timoshenko shear calculations.
    section.shear_area = area

    return section


def _get_youngs_modulus(
    material=None,
    youngs_modulus=None,
):
    """
    Obtain axial Young's modulus from either a Material object
    or the legacy direct Young's modulus input.
    """

    if material is not None:

        value = getattr(
            material,
            "axial_youngs_modulus",
            None,
        )

        if value is None:

            value = getattr(
                material,
                "youngs_modulus",
                None,
            )

        if value is not None:
            return value

    if youngs_modulus is not None:

        if youngs_modulus <= 0:
            raise ValueError(
                "Young's modulus must be positive."
            )

        return youngs_modulus

    raise ValueError(
        "Young's modulus is required. "
        "Supply a material or youngs_modulus."
    )


def _get_shear_modulus(material):
    """
    Return shear modulus where available.
    """

    if material is None:
        return None

    return getattr(
        material,
        "shear_modulus",
        None,
    )


def _calculate_bending_stress(
    max_moment,
    section,
):
    """
    Calculate bending stress when section modulus
    is available.

    Some manufacturer catalogue sections currently
    have no validated section modulus in the source
    data.

    In that situation the structural response can
    still be calculated, but bending stress is
    unavailable.
    """

    section_modulus = getattr(
        section,
        "section_modulus",
        None,
    )

    if section_modulus is None:
        return None

    if section_modulus <= 0:
        raise ValueError(
            "Section modulus must be positive."
        )

    return max_moment / section_modulus


def calculate_beam(
    span,
    load=None,
    width=None,
    height=None,
    youngs_modulus=None,
    support_condition=SupportCondition.SIMPLY_SUPPORTED,
    material=None,
    section=None,
    point_load=None,
):
    """
    Calculate a beam subjected to a central point load.

    Supports both the original interface:

        calculate_beam(
            span=...,
            load=...,
            width=...,
            height=...,
            youngs_modulus=...
        )

    and the new section-based interface:

        calculate_beam(
            span=...,
            point_load=...,
            material=...,
            section=...
        )

    Euler-Bernoulli beam theory is used.
    """

    if span <= 0:
        raise ValueError(
            "Span must be positive."
        )

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    if point_load is not None:
        load_value = point_load
    else:
        load_value = load

    if load_value is None:
        raise ValueError(
            "Point load is required."
        )

    if load_value < 0:
        raise ValueError(
            "Load must be non-negative."
        )

    # ---------------------------------------------------------
    # Section
    # ---------------------------------------------------------

    if section is None:

        if width is None or height is None:
            raise ValueError(
                "Either section or width and height "
                "must be supplied."
            )

        section = _rectangular_section(
            width,
            height,
        )

    # ---------------------------------------------------------
    # Material
    # ---------------------------------------------------------

    E = _get_youngs_modulus(
        material=material,
        youngs_modulus=youngs_modulus,
    )

    # ---------------------------------------------------------
    # Section stiffness
    # ---------------------------------------------------------

    I = _get_section_property(
        section,
        "second_moment_of_area",
    )

    if I <= 0:
        raise ValueError(
            "Second moment of area must be positive."
        )

    # ---------------------------------------------------------
    # Simply supported beam
    # ---------------------------------------------------------

    if (
        support_condition
        == SupportCondition.SIMPLY_SUPPORTED
    ):

        left_reaction = (
            load_value / 2
        )

        right_reaction = (
            load_value / 2
        )

        max_bending_moment = (
            load_value * span / 4
        )

        bending_deflection = (
            load_value
            * span**3
            / (48 * E * I)
        )

    # ---------------------------------------------------------
    # Fixed-fixed beam
    # ---------------------------------------------------------

    elif (
        support_condition
        == SupportCondition.FIXED_FIXED
    ):

        left_reaction = (
            load_value / 2
        )

        right_reaction = (
            load_value / 2
        )

        max_bending_moment = (
            load_value * span / 8
        )

        bending_deflection = (
            load_value
            * span**3
            / (192 * E * I)
        )

    else:

        raise ValueError(
            f"Unsupported support condition: "
            f"{support_condition}"
        )

    # ---------------------------------------------------------
    # Stress
    # ---------------------------------------------------------

    section_modulus = getattr(
        section,
        "section_modulus",
        None,
    )

    bending_stress = _calculate_bending_stress(
        max_bending_moment,
        section,
    )

    return BeamPointLoadResult(
        left_reaction=left_reaction,
        right_reaction=right_reaction,
        max_bending_moment=max_bending_moment,
        bending_stress=bending_stress,
        second_moment_of_area=I,
        section_modulus=section_modulus,
        max_deflection=bending_deflection,
    )


def calculate_beam_udl(
    span,
    distributed_load=None,
    width=None,
    height=None,
    youngs_modulus=None,
    support_condition=SupportCondition.SIMPLY_SUPPORTED,
    material=None,
    section=None,
    shear_correction_factor=5 / 6,
):
    """
    Calculate a beam subjected to a uniformly distributed load.

    Supports both the original width/height interface and
    the new section-based interface.

    Original interface:

        calculate_beam_udl(
            span=...,
            distributed_load=...,
            width=...,
            height=...,
            material=...
        )

    New interface:

        calculate_beam_udl(
            span=...,
            distributed_load=...,
            material=...,
            section=...
        )
    """

    # ---------------------------------------------------------
    # Input validation
    # ---------------------------------------------------------

    if span <= 0:
        raise ValueError(
            "Span must be positive."
        )

    if distributed_load is None:
        raise ValueError(
            "Distributed load is required."
        )

    if distributed_load < 0:
        raise ValueError(
            "Distributed load must be non-negative."
        )

    # ---------------------------------------------------------
    # Section
    # ---------------------------------------------------------

    if section is None:

        if width is None or height is None:
            raise ValueError(
                "Either section or width and height "
                "must be supplied."
            )

        section = _rectangular_section(
            width,
            height,
        )

    # ---------------------------------------------------------
    # Material
    # ---------------------------------------------------------

    E = _get_youngs_modulus(
        material=material,
        youngs_modulus=youngs_modulus,
    )

    # ---------------------------------------------------------
    # Section stiffness
    # ---------------------------------------------------------

    I = _get_section_property(
        section,
        "second_moment_of_area",
    )

    if I <= 0:
        raise ValueError(
            "Second moment of area must be positive."
        )

    # ---------------------------------------------------------
    # Total load
    # ---------------------------------------------------------

    total_load = (
        distributed_load * span
    )

    # ---------------------------------------------------------
    # Simply supported
    # ---------------------------------------------------------

    if (
        support_condition
        == SupportCondition.SIMPLY_SUPPORTED
    ):

        left_reaction = (
            total_load / 2
        )

        right_reaction = (
            total_load / 2
        )

        max_bending_moment = (
            distributed_load
            * span**2
            / 8
        )

        bending_deflection = (
            5
            * distributed_load
            * span**4
            / (384 * E * I)
        )

    # ---------------------------------------------------------
    # Fixed-fixed
    # ---------------------------------------------------------

    elif (
        support_condition
        == SupportCondition.FIXED_FIXED
    ):

        left_reaction = (
            total_load / 2
        )

        right_reaction = (
            total_load / 2
        )

        max_bending_moment = (
            distributed_load
            * span**2
            / 12
        )

        bending_deflection = (
            distributed_load
            * span**4
            / (384 * E * I)
        )

    else:

        raise ValueError(
            f"Unsupported support condition: "
            f"{support_condition}"
        )

    # ---------------------------------------------------------
    # Bending stress
    # ---------------------------------------------------------

    section_modulus = getattr(
        section,
        "section_modulus",
        None,
    )

    bending_stress = _calculate_bending_stress(
        max_bending_moment,
        section,
    )

    # ---------------------------------------------------------
    # Timoshenko shear deflection
    # ---------------------------------------------------------

    shear_deflection = 0.0

    shear_area = getattr(
        section,
        "shear_area",
        None,
    )

    shear_modulus = _get_shear_modulus(
        material
    )

    # At present, shear deflection is enabled only
    # for simply supported UDL beams.
    #
    # For catalogue profiles, shear_area must be
    # explicitly supplied before this contribution
    # is enabled.

    if (
        support_condition
        == SupportCondition.SIMPLY_SUPPORTED
        and shear_area is not None
        and shear_modulus is not None
    ):

        shear_deflection = (
            calculate_shear_deflection_udl(
                span=span,
                distributed_load=distributed_load,
                shear_modulus=shear_modulus,
                shear_area=shear_area,
                shear_correction_factor=
                    shear_correction_factor,
            )
        )

    # ---------------------------------------------------------
    # Total deflection
    # ---------------------------------------------------------

    max_deflection = (
        bending_deflection
        + shear_deflection
    )

    # ---------------------------------------------------------
    # Shear contribution
    # ---------------------------------------------------------

    if max_deflection > 0:

        shear_contribution = (
            shear_deflection
            / max_deflection
            * 100
        )

    else:

        shear_contribution = 0.0

    # ---------------------------------------------------------
    # Diagrams
    # ---------------------------------------------------------

    diagram_results = calculate_beam_diagrams(
        span=span,
        distributed_load=distributed_load,
        width=width,
        height=height,
        youngs_modulus=E,
        support_condition=support_condition,
        material=material,
        section=section,
    )

    x = diagram_results["x"]
    shear = diagram_results["shear"]
    moment = diagram_results["moment"]
    deflection = diagram_results["deflection"]

    # ---------------------------------------------------------
    # Results object
    # ---------------------------------------------------------

    return BeamUDLResult(
        distributed_load=distributed_load,
        total_load=total_load,
        left_reaction=left_reaction,
        right_reaction=right_reaction,
        max_bending_moment=max_bending_moment,
        bending_stress=bending_stress,
        second_moment_of_area=I,
        section_modulus=section_modulus,
        bending_deflection=bending_deflection,
        shear_deflection=shear_deflection,
        max_deflection=max_deflection,
        shear_contribution=shear_contribution,
        x=x,
        shear=shear,
        moment=moment,
        deflection=deflection,
    )


def calculate_beam_diagrams(
    span,
    distributed_load=None,
    width=None,
    height=None,
    youngs_modulus=None,
    support_condition=SupportCondition.SIMPLY_SUPPORTED,
    material=None,
    section=None,
    n_points=101,
):
    """
    Generate shear-force, bending-moment and
    Euler-Bernoulli bending-deflection diagrams.

    Three interfaces are supported.

    1. Standalone legacy:

        calculate_beam_diagrams(
            span=2.0,
            distributed_load=2000.0
        )

    2. Legacy geometry:

        calculate_beam_diagrams(
            span=2.0,
            distributed_load=2000.0,
            width=0.1,
            height=0.15,
            youngs_modulus=25e9
        )

    3. New section-based:

        calculate_beam_diagrams(
            span=2.0,
            distributed_load=2000.0,
            material=material,
            section=section
        )

    Returns a dictionary for backwards compatibility.
    """

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    if span <= 0:
        raise ValueError(
            "Span must be positive."
        )

    if distributed_load is None:
        raise ValueError(
            "Distributed load is required."
        )

    if distributed_load < 0:
        raise ValueError(
            "Distributed load must be non-negative."
        )

    # ---------------------------------------------------------
    # Standalone legacy mode
    # ---------------------------------------------------------
    #
    # Existing test:
    #
    # calculate_beam_diagrams(
    #     span=2.0,
    #     distributed_load=2000.0
    # )
    #
    # This mode only requires shear and moment.
    # ---------------------------------------------------------

    standalone_mode = (
        section is None
        and width is None
        and height is None
        and material is None
        and youngs_modulus is None
    )

    if standalone_mode:

        x = np.linspace(
            0.0,
            span,
            n_points,
        )

        if (
            support_condition
            == SupportCondition.SIMPLY_SUPPORTED
        ):

            left_reaction = (
                distributed_load
                * span
                / 2
            )

            shear = (
                left_reaction
                - distributed_load * x
            )

            moment = (
                left_reaction * x
                - distributed_load * x**2 / 2
            )

        elif (
            support_condition
            == SupportCondition.FIXED_FIXED
        ):

            left_reaction = (
                distributed_load
                * span
                / 2
            )

            shear = (
                left_reaction
                - distributed_load * x
            )

            moment = (
                distributed_load
                * x
                * (span - x)
                / 2
                - distributed_load
                * span**2
                / 12
            )

        else:

            raise ValueError(
                f"Unsupported support condition: "
                f"{support_condition}"
            )

        return {
            "x": x,
            "shear": shear,
            "moment": moment,
        }

    # ---------------------------------------------------------
    # Section-based / geometry mode
    # ---------------------------------------------------------

    if section is None:

        if width is None or height is None:
            raise ValueError(
                "Either section or width and height "
                "must be supplied."
            )

        section = _rectangular_section(
            width,
            height,
        )

    # ---------------------------------------------------------
    # Young's modulus
    # ---------------------------------------------------------

    E = _get_youngs_modulus(
        material=material,
        youngs_modulus=youngs_modulus,
    )

    # ---------------------------------------------------------
    # Section stiffness
    # ---------------------------------------------------------

    I = _get_section_property(
        section,
        "second_moment_of_area",
    )

    if I <= 0:
        raise ValueError(
            "Second moment of area must be positive."
        )

    # ---------------------------------------------------------
    # Coordinate array
    # ---------------------------------------------------------

    x = np.linspace(
        0.0,
        span,
        n_points,
    )

    # ---------------------------------------------------------
    # Simply supported beam
    # ---------------------------------------------------------

    if (
        support_condition
        == SupportCondition.SIMPLY_SUPPORTED
    ):

        left_reaction = (
            distributed_load
            * span
            / 2
        )

        shear = (
            left_reaction
            - distributed_load * x
        )

        moment = (
            left_reaction * x
            - distributed_load * x**2 / 2
        )

        deflection = (
            distributed_load
            * x
            * (
                span**3
                - 2 * span * x**2
                + x**3
            )
            / (24 * E * I)
        )

    # ---------------------------------------------------------
    # Fixed-fixed beam
    # ---------------------------------------------------------

    elif (
        support_condition
        == SupportCondition.FIXED_FIXED
    ):

        left_reaction = (
            distributed_load
            * span
            / 2
        )

        shear = (
            left_reaction
            - distributed_load * x
        )

        moment = (
            distributed_load
            * x
            * (span - x)
            / 2
            - distributed_load
            * span**2
            / 12
        )

        deflection = (
            distributed_load
            * x**2
            * (span - x)**2
            / (24 * E * I)
        )

    else:

        raise ValueError(
            f"Unsupported support condition: "
            f"{support_condition}"
        )

    # ---------------------------------------------------------
    # Return dictionary
    # ---------------------------------------------------------

    return {
        "x": x,
        "shear": shear,
        "moment": moment,
        "deflection": deflection,
    }