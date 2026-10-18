def calculate_shear_deflection_udl(
    span,
    distributed_load,
    shear_modulus,
    shear_area,
    shear_correction_factor=5 / 6
):
    """
    Calculate the shear deflection contribution for a
    simply supported beam under a uniformly distributed load.

    Based on Timoshenko beam theory.

    Parameters
    ----------
    span : float
        Beam span in metres.

    distributed_load : float
        Uniformly distributed load in N/m.

    shear_modulus : float
        Effective shear modulus in Pa.

    shear_area : float
        Effective shear area in m².

    shear_correction_factor : float
        Shear correction factor (dimensionless).

    Returns
    -------
    float
        Maximum shear deflection in metres.

    NOTE:
    For GRP composite profiles, the shear modulus, effective shear
    area and correction factor must be validated for the specific
    section and laminate construction.
    """

    if span <= 0:
        raise ValueError(
            "Span must be greater than zero."
        )

    if distributed_load < 0:
        raise ValueError(
            "Distributed load cannot be negative."
        )

    if shear_modulus <= 0:
        raise ValueError(
            "Shear modulus must be greater than zero."
        )

    if shear_area <= 0:
        raise ValueError(
            "Shear area must be greater than zero."
        )

    if shear_correction_factor <= 0:
        raise ValueError(
            "Shear correction factor must be greater than zero."
        )

    shear_deflection = (
        distributed_load
        * span**2
        / (
            8
            * shear_correction_factor
            * shear_area
            * shear_modulus
        )
    )

    return shear_deflection

def calculate_shear_contribution(
    bending_deflection,
    shear_deflection
):
    """
    Calculate the percentage contribution of shear
    deformation to total deflection.

    Parameters
    ----------
    bending_deflection : float
        Euler-Bernoulli bending deflection in metres.

    shear_deflection : float
        Timoshenko shear deflection in metres.

    Returns
    -------
    float
        Shear contribution as a percentage of total deflection.

    Material properties and section properties used elsewhere
    in the calculation are generic/placeholders until validated
    against manufacturer datasheets or appropriate test data.
    """

    if bending_deflection < 0:
        raise ValueError(
            "Bending deflection cannot be negative."
        )

    if shear_deflection < 0:
        raise ValueError(
            "Shear deflection cannot be negative."
        )

    total_deflection = (
        bending_deflection
        + shear_deflection
    )

    if total_deflection == 0:
        return 0.0

    return (
        shear_deflection
        / total_deflection
        * 100
    )