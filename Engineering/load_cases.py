from dataclasses import dataclass


# ============================================================
# LOAD CASE RESULT OBJECTS
# ============================================================

@dataclass(frozen=True)
class SLSLoadCase:
    permanent_line_load: float
    variable_line_load: float
    total_line_load: float
    total_load: float
    left_reaction: float
    right_reaction: float
    max_bending_moment: float


@dataclass(frozen=True)
class ULSLoadCase:
    permanent_line_load: float
    variable_line_load: float
    total_line_load: float
    total_load: float
    left_reaction: float
    right_reaction: float
    max_bending_moment: float
    gamma_g: float
    gamma_q: float


# ============================================================
# SELF-WEIGHT
# ============================================================

def calculate_self_weight_line_load(
    section,
    material=None,
    gravity=9.81,
):
    """
    Calculate section self-weight as a line load.

    Priority:

    1. Use section.mass_per_length if available.
    2. Otherwise use material.density * section.area.
    3. If neither is available, return zero.

    Units:
        mass_per_length : kg/m
        density          : kg/m³
        area             : m²
        gravity          : m/s²
        result           : N/m
    """

    if section is None:
        raise ValueError("Section must be provided.")

    if gravity <= 0:
        raise ValueError(
            "Gravity must be greater than zero."
        )

    # --------------------------------------------------------
    # Method 1:
    # Manufacturer/profile mass per unit length
    # --------------------------------------------------------

    mass_per_length = getattr(
        section,
        "mass_per_length",
        None,
    )

    if mass_per_length is not None:

        if mass_per_length < 0:
            raise ValueError(
                "Mass per length cannot be negative."
            )

        return mass_per_length * gravity

    # --------------------------------------------------------
    # Method 2:
    # Material density × section area
    # --------------------------------------------------------

    density = None
    area = getattr(
        section,
        "area",
        None,
    )

    if material is not None:
        density = getattr(
            material,
            "density",
            None,
        )

    if density is not None and area is not None:

        if density < 0:
            raise ValueError(
                "Material density cannot be negative."
            )

        if area < 0:
            raise ValueError(
                "Section area cannot be negative."
            )

        return density * area * gravity

    # --------------------------------------------------------
    # No self-weight information available
    # --------------------------------------------------------

    return 0.0


# ============================================================
# POINT LOAD
# ============================================================

def analyse_point_load(
    span,
    load,
    width,
    height,
    youngs_modulus,
):
    """
    Compatibility interface for point-load beam analysis.

    Simply-supported beam with a central point load.

    Returns basic reaction and bending-moment information.
    """

    if span <= 0:
        raise ValueError(
            "Span must be greater than zero."
        )

    if load < 0:
        raise ValueError(
            "Load cannot be negative."
        )

    if width <= 0:
        raise ValueError(
            "Width must be greater than zero."
        )

    if height <= 0:
        raise ValueError(
            "Height must be greater than zero."
        )

    if youngs_modulus <= 0:
        raise ValueError(
            "Young's modulus must be greater than zero."
        )

    left_reaction = load / 2
    right_reaction = load / 2

    max_bending_moment = (
        load * span / 4
    )

    return {
        "left_reaction": left_reaction,
        "right_reaction": right_reaction,
        "max_bending_moment": max_bending_moment,
    }


# ============================================================
# UDL
# ============================================================

def analyse_udl(
    span,
    distributed_load,
    width,
    height,
    material,
):
    """
    Compatibility interface for UDL beam analysis.

    Simply-supported beam under a uniformly distributed load.

    The detailed structural calculation is handled by
    Engineering.beam_analysis.
    """

    if span <= 0:
        raise ValueError(
            "Span must be greater than zero."
        )

    if distributed_load < 0:
        raise ValueError(
            "Distributed load cannot be negative."
        )

    if width <= 0:
        raise ValueError(
            "Width must be greater than zero."
        )

    if height <= 0:
        raise ValueError(
            "Height must be greater than zero."
        )

    if material is None:
        raise ValueError(
            "Material must be provided."
        )

    total_load = (
        distributed_load * span
    )

    left_reaction = (
        total_load / 2
    )

    right_reaction = (
        total_load / 2
    )

    max_bending_moment = (
        distributed_load * span**2 / 8
    )

    return {
        "distributed_load": distributed_load,
        "total_load": total_load,
        "left_reaction": left_reaction,
        "right_reaction": right_reaction,
        "max_bending_moment": max_bending_moment,
    }


# ============================================================
# SLS / ULS LOAD COMBINATIONS
# ============================================================

def calculate_load_cases(
    span,
    tributary_width,
    self_weight_line_load,
    permanent_area_load,
    variable_area_load,
    gamma_g=1.35,
    gamma_q=1.50,
):
    """
    Calculate prototype SLS and ULS load combinations.

    SLS:
        Gk + Qk

    ULS:
        gamma_G * Gk + gamma_Q * Qk

    This is a prototype load-combination implementation and
    does not by itself constitute full Eurocode compliance.
    """

    if span <= 0:
        raise ValueError(
            "Span must be greater than zero."
        )

    if tributary_width <= 0:
        raise ValueError(
            "Tributary width must be greater than zero."
        )

    if self_weight_line_load < 0:
        raise ValueError(
            "Self-weight line load cannot be negative."
        )

    if permanent_area_load < 0:
        raise ValueError(
            "Permanent area load cannot be negative."
        )

    if variable_area_load < 0:
        raise ValueError(
            "Variable area load cannot be negative."
        )

    if gamma_g <= 0:
        raise ValueError(
            "gamma_g must be greater than zero."
        )

    if gamma_q <= 0:
        raise ValueError(
            "gamma_q must be greater than zero."
        )

    # --------------------------------------------------------
    # Convert area loads to line loads
    # --------------------------------------------------------

    permanent_area_line_load = (
        permanent_area_load
        * tributary_width
    )

    variable_area_line_load = (
        variable_area_load
        * tributary_width
    )

    # --------------------------------------------------------
    # Characteristic loads
    # --------------------------------------------------------

    permanent_line_load = (
        self_weight_line_load
        + permanent_area_line_load
    )

    variable_line_load = (
        variable_area_line_load
    )

    # --------------------------------------------------------
    # SLS
    # --------------------------------------------------------

    sls_line_load = (
        permanent_line_load
        + variable_line_load
    )

    sls_total_load = (
        sls_line_load * span
    )

    sls_left_reaction = (
        sls_total_load / 2
    )

    sls_right_reaction = (
        sls_total_load / 2
    )

    sls_max_bending_moment = (
        sls_line_load * span**2 / 8
    )

    sls = SLSLoadCase(
        permanent_line_load=permanent_line_load,
        variable_line_load=variable_line_load,
        total_line_load=sls_line_load,
        total_load=sls_total_load,
        left_reaction=sls_left_reaction,
        right_reaction=sls_right_reaction,
        max_bending_moment=sls_max_bending_moment,
    )

    # --------------------------------------------------------
    # ULS
    # --------------------------------------------------------

    uls_permanent_line_load = (
        gamma_g * permanent_line_load
    )

    uls_variable_line_load = (
        gamma_q * variable_line_load
    )

    uls_line_load = (
        uls_permanent_line_load
        + uls_variable_line_load
    )

    uls_total_load = (
        uls_line_load * span
    )

    uls_left_reaction = (
        uls_total_load / 2
    )

    uls_right_reaction = (
        uls_total_load / 2
    )

    uls_max_bending_moment = (
        uls_line_load * span**2 / 8
    )

    uls = ULSLoadCase(
        permanent_line_load=uls_permanent_line_load,
        variable_line_load=uls_variable_line_load,
        total_line_load=uls_line_load,
        total_load=uls_total_load,
        left_reaction=uls_left_reaction,
        right_reaction=uls_right_reaction,
        max_bending_moment=uls_max_bending_moment,
        gamma_g=gamma_g,
        gamma_q=gamma_q,
    )

    # --------------------------------------------------------
    # Complete result
    # --------------------------------------------------------

    return {
        "span": span,
        "tributary_width": tributary_width,

        "self_weight_line_load": self_weight_line_load,

        "permanent_area_load": permanent_area_load,
        "variable_area_load": variable_area_load,

        "permanent_area_line_load": permanent_area_line_load,
        "variable_area_line_load": variable_area_line_load,

        "permanent_line_load": permanent_line_load,
        "variable_line_load": variable_line_load,

        "gamma_g": gamma_g,
        "gamma_q": gamma_q,

        "sls_line_load": sls_line_load,
        "uls_line_load": uls_line_load,

        "sls_total_load": sls_total_load,
        "uls_total_load": uls_total_load,

        "SLS": sls,
        "ULS": uls,
    }