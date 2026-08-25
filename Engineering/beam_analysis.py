def calculate_beam(
    span,
    load,
    width,
    height,
    youngs_modulus
):
    """
    Analyse a simply supported beam with a central point load.

    All inputs use SI units:
    span              : m
    load              : N
    width             : m
    height            : m
    youngs_modulus    : Pa
    """
        # Input validation
    if span <= 0:
        raise ValueError("Span must be greater than zero.")

    if load < 0:
        raise ValueError("Load cannot be negative.")

    if width <= 0:
        raise ValueError("Width must be greater than zero.")

    if height <= 0:
        raise ValueError("Height must be greater than zero.")

    if youngs_modulus <= 0:
        raise ValueError("Young's modulus must be greater than zero.")

    # Support reactions
    left_reaction = load / 2
    right_reaction = load / 2

    # Maximum bending moment
    max_bending_moment = (load * span) / 4

    # Second moment of area
    second_moment_of_area = (width * height**3) / 12

    # Section modulus
    section_modulus = (width * height**2) / 6

    # Maximum bending stress
    bending_stress = max_bending_moment / section_modulus

    # Maximum deflection
    max_deflection = (
        load * span**3
        / (48 * youngs_modulus * second_moment_of_area)
    )

    return {
        "left_reaction": left_reaction,
        "right_reaction": right_reaction,
        "max_bending_moment": max_bending_moment,
        "second_moment_of_area": second_moment_of_area,
        "section_modulus": section_modulus,
        "bending_stress": bending_stress,
        "max_deflection": max_deflection,
    }

def calculate_beam_udl(
    span,
    distributed_load,
    width,
    height,
    youngs_modulus
):
    """
    Analyse a simply supported beam under a uniformly
    distributed load.

    All inputs use SI units:
    span              : m
    distributed_load  : N/m
    width             : m
    height            : m
    youngs_modulus    : Pa
    """

    # Input validation
    if span <= 0:
        raise ValueError("Span must be greater than zero.")

    if distributed_load < 0:
        raise ValueError("Distributed load cannot be negative.")

    if width <= 0:
        raise ValueError("Width must be greater than zero.")

    if height <= 0:
        raise ValueError("Height must be greater than zero.")

    if youngs_modulus <= 0:
        raise ValueError("Young's modulus must be greater than zero.")

    # Support reactions
    total_load = distributed_load * span
    left_reaction = total_load / 2
    right_reaction = total_load / 2

    # Maximum bending moment
    max_bending_moment = (
        distributed_load * span**2
    ) / 8

    # Section properties
    second_moment_of_area = (
        width * height**3
    ) / 12

    section_modulus = (
        width * height**2
    ) / 6

    # Maximum bending stress
    bending_stress = (
        max_bending_moment / section_modulus
    )

    # Maximum deflection
    max_deflection = (
        5 * distributed_load * span**4
    ) / (
        384
        * youngs_modulus
        * second_moment_of_area
    )

    return {
        "total_load": total_load,
        "left_reaction": left_reaction,
        "right_reaction": right_reaction,
        "max_bending_moment": max_bending_moment,
        "second_moment_of_area": second_moment_of_area,
        "section_modulus": section_modulus,
        "bending_stress": bending_stress,
        "max_deflection": max_deflection,
    }