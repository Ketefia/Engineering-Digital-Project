from Engineering.calculation_model import CalculationInput, CalculationSummary
from Engineering.panel_analysis import check_panel_design
from Engineering.supports import SupportCondition


def build_panel_calculation(
    span,
    tributary_width,
    permanent_load,
    imposed_load,
    gamma_G,
    gamma_Q,
    support_condition,
    material_record,
    profile,
    allowable_stress,
    allowable_deflection,
    shear_correction_factor=5 / 6,
):
    """
    Build a complete ULS/SLS panel calculation.

    Loads are entered as characteristic area loads in N/m².

    ULS:
        gamma_G * Gk + gamma_Q * Qk

    SLS:
        Gk + Qk

    The resulting area loads are converted to line loads using
    the tributary width.
    """

    # ---------------------------------------------------------
    # Basic validation
    # ---------------------------------------------------------

    if span <= 0:
        raise ValueError("Span must be greater than zero.")

    if tributary_width <= 0:
        raise ValueError("Tributary width must be greater than zero.")

    if permanent_load < 0:
        raise ValueError("Permanent load cannot be negative.")

    if imposed_load < 0:
        raise ValueError("Imposed load cannot be negative.")

    if gamma_G <= 0:
        raise ValueError("gamma_G must be greater than zero.")

    if gamma_Q <= 0:
        raise ValueError("gamma_Q must be greater than zero.")

    if allowable_stress <= 0:
        raise ValueError("Allowable stress must be greater than zero.")

    if allowable_deflection <= 0:
        raise ValueError("Allowable deflection must be greater than zero.")

    if shear_correction_factor <= 0:
        raise ValueError(
            "Shear correction factor must be greater than zero."
        )

    # ---------------------------------------------------------
    # Resolve support condition
    # ---------------------------------------------------------

    if isinstance(support_condition, SupportCondition):
        resolved_support = support_condition
    else:
        try:
            resolved_support = SupportCondition(support_condition)
        except ValueError:
            valid_values = [
                condition.value for condition in SupportCondition
            ]
            raise ValueError(
                f"Invalid support condition '{support_condition}'. "
                f"Expected one of: {valid_values}"
            )

    # ---------------------------------------------------------
    # Material
    # ---------------------------------------------------------

    material = material_record.get_material()

    # ---------------------------------------------------------
    # Load cases
    # ---------------------------------------------------------

    uls_area_load = (
        gamma_G * permanent_load
        + gamma_Q * imposed_load
    )

    sls_area_load = permanent_load + imposed_load

    # ---------------------------------------------------------
    # ULS calculation
    # ---------------------------------------------------------

    uls_design = check_panel_design(
        span=span,
        tributary_width=tributary_width,
        area_load=uls_area_load,
        material=material,
        section=profile,
        support_condition=resolved_support,
        allowable_stress=allowable_stress,
        allowable_deflection=allowable_deflection,
        shear_correction_factor=shear_correction_factor,
    )

    # ---------------------------------------------------------
    # SLS calculation
    # ---------------------------------------------------------

    sls_design = check_panel_design(
        span=span,
        tributary_width=tributary_width,
        area_load=sls_area_load,
        material=material,
        section=profile,
        support_condition=resolved_support,
        allowable_stress=allowable_stress,
        allowable_deflection=allowable_deflection,
        shear_correction_factor=shear_correction_factor,
    )

    # ---------------------------------------------------------
    # Provenance
    # ---------------------------------------------------------

    material_name = getattr(
        material_record,
        "name",
        getattr(material, "name", "Unknown material"),
    )

    material_manufacturer = getattr(
        material_record,
        "manufacturer",
        "Unknown",
    )

    material_grade = getattr(
        material_record,
        "standard_grade",
        "Unknown",
    )

    material_validation_status = getattr(
        material_record,
        "validation_status",
        "Validation status not specified",
    )

    profile_name = getattr(
        profile,
        "designation",
        getattr(profile, "name", "Custom section"),
    )

    profile_source = getattr(
        profile,
        "source",
        "User-defined section",
    )

    profile_validation_status = getattr(
        profile,
        "validation_status",
        "Validation status not specified",
    )

    calculation_input = CalculationInput(
        span=span,
        tributary_width=tributary_width,
        permanent_load=permanent_load,
        imposed_load=imposed_load,
        gamma_G=gamma_G,
        gamma_Q=gamma_Q,
        support_condition=resolved_support.value,
        material_name=material_name,
        material_manufacturer=material_manufacturer,
        material_grade=material_grade,
        material_validation_status=material_validation_status,
        profile_name=profile_name,
        profile_source=profile_source,
        profile_validation_status=profile_validation_status,
    )

    # ---------------------------------------------------------
    # Assumptions
    # ---------------------------------------------------------

    assumptions = [
        "Euler-Bernoulli beam theory is used for bending behaviour.",
        "The panel strip is treated as a simply supported or fixed-fixed beam according to the selected support condition.",
        "The applied area load is converted to line load using the tributary width.",
        "Material properties are treated as engineering input data and require validation against the applicable manufacturer documentation.",
        "The current strength check is an allowable-stress-style prototype check and is not a full Eurocode GRP resistance calculation.",
        "Local buckling, web/flange instability, connection behaviour and stress concentrations are not included.",
    ]

    # ---------------------------------------------------------
    # Warnings
    # ---------------------------------------------------------

    warnings = [
        "This calculation is a prototype engineering tool and does not constitute a certified structural design.",
        "Manufacturer material and profile properties must be verified before engineering use.",
    ]

    # Effective flexural modulus warning
    standard_grade = str(material_grade).upper()

    if "E23" in standard_grade:
        warnings.append(
            "The published E23 value is an effective flexural modulus "
            "for the pultruded profile system; it should not automatically "
            "be interpreted as a generic isotropic Young's modulus."
        )

    # Shear warning
    if getattr(material, "shear_modulus", None) is None:
        warnings.append(
            "Shear modulus G is not available for the selected material. "
            "Timoshenko shear deflection is therefore not included."
        )

    # Profile shear-area warning
    if getattr(profile, "shear_area", None) is not None:
        warnings.append(
            "Shear-area treatment for the selected profile should be "
            "validated against manufacturer/test data before relying on "
            "Timoshenko shear deformation."
        )

    # ---------------------------------------------------------
    # Overall result
    # ---------------------------------------------------------

    overall_pass = (
        uls_design["overall_pass"]
        and sls_design["deflection_check"].passes
    )

    return CalculationSummary(
        inputs=calculation_input,
        uls_results=uls_design["panel_results"],
        sls_results=sls_design["panel_results"],
        uls_stress_check=uls_design["stress_check"],
        sls_deflection_check=sls_design["deflection_check"],
        overall_pass=overall_pass,
        assumptions=assumptions,
        warnings=warnings,
    )