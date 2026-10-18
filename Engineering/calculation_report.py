from datetime import datetime


def _format_number(value, decimals=3):
    """
    Format a numerical value for engineering reporting.
    """
    if value is None:
        return "N/A"

    return f"{value:.{decimals}f}"


def _format_force(value):
    """
    Format force in N and kN.
    """
    if value is None:
        return "N/A"

    if abs(value) >= 1000:
        return f"{value / 1000:.3f} kN"

    return f"{value:.1f} N"


def _format_moment(value):
    """
    Format bending moment in N·m and kN·m.
    """
    if value is None:
        return "N/A"

    if abs(value) >= 1000:
        return f"{value / 1000:.3f} kN·m"

    return f"{value:.1f} N·m"


def _format_stress(value):
    """
    Format stress in Pa / MPa.
    """
    if value is None:
        return "N/A"

    return f"{value / 1e6:.3f} MPa"


def _format_deflection(value):
    """
    Format deflection in mm.
    """
    if value is None:
        return "N/A"

    return f"{value * 1000:.3f} mm"


def _format_load(value):
    """
    Format area load in kN/m².
    """
    if value is None:
        return "N/A"

    return f"{value / 1000:.3f} kN/m²"


def _check_status(check):
    """
    Return readable check status.
    """
    return "PASS" if check.passes else "FAIL"


def generate_calculation_report(calculation):
    """
    Generate a Markdown engineering calculation report.

    Parameters
    ----------
    calculation:
        CalculationSummary instance.

    Returns
    -------
    str
        Markdown-formatted calculation report.
    """

    inputs = calculation.inputs
    uls = calculation.uls_results
    sls = calculation.sls_results

    lines = []

    # ==============================================================
    # Header
    # ==============================================================

    lines.append("# GRP Structural Design Calculation")
    lines.append("")

    lines.append(
        f"**Calculation ID:** {calculation.calculation_id}"
    )

    lines.append(
        f"**Calculation timestamp:** "
        f"{calculation.calculation_timestamp}"
    )

    lines.append(
        f"**Overall status:** **{calculation.status()}**"
    )

    lines.append("")

    lines.append(
        "> Prototype engineering calculation. "
        "Material properties, profile properties and design assumptions "
        "must be validated before engineering use."
    )

    lines.append("")

    # ==============================================================
    # 1. Structural arrangement
    # ==============================================================

    lines.append("## 1. Structural arrangement")
    lines.append("")

    lines.append(
        f"- Support condition: **{inputs.support_condition}**"
    )

    lines.append(
        f"- Span: **{_format_number(inputs.span, 3)} m**"
    )

    lines.append(
        f"- Tributary width: "
        f"**{_format_number(inputs.tributary_width, 3)} m**"
    )

    lines.append("")

    # ==============================================================
    # 2. Material
    # ==============================================================

    lines.append("## 2. Material")
    lines.append("")

    lines.append(
        f"- Material: **{inputs.material_name}**"
    )

    lines.append(
        f"- Manufacturer: **{inputs.material_manufacturer}**"
    )

    lines.append(
        f"- Grade/designation: **{inputs.material_grade}**"
    )

    lines.append(
        f"- Validation status: **{inputs.material_validation_status}**"
    )

    lines.append("")

    # ==============================================================
    # 3. Profile
    # ==============================================================

    lines.append("## 3. Structural profile")
    lines.append("")

    lines.append(
        f"- Profile: **{inputs.profile_name}**"
    )

    lines.append(
        f"- Profile source: **{inputs.profile_source}**"
    )

    lines.append(
        f"- Profile validation status: "
        f"**{inputs.profile_validation_status}**"
    )

    lines.append("")

    # ==============================================================
    # 4. Loading
    # ==============================================================

    lines.append("## 4. Loading")
    lines.append("")

    lines.append(
        f"- Characteristic permanent load: "
        f"**{_format_load(inputs.permanent_load)}**"
    )

    lines.append(
        f"- Characteristic imposed load: "
        f"**{_format_load(inputs.imposed_load)}**"
    )

    lines.append(
        f"- ULS factor γG: **{_format_number(inputs.gamma_G, 3)}**"
    )

    lines.append(
        f"- ULS factor γQ: **{_format_number(inputs.gamma_Q, 3)}**"
    )

    lines.append("")

    # ==============================================================
    # 5. ULS
    # ==============================================================

    lines.append("## 5. Ultimate limit state")
    lines.append("")

    lines.append(
        "The ULS calculation uses:"
    )

    lines.append("")

    lines.append(
        f"**qULS = γG · Gk + γQ · Qk**"
    )

    lines.append("")

    lines.append(
        f"- ULS distributed load: "
        f"**{_format_load(uls.distributed_load)}**"
    )

    lines.append(
        f"- Total ULS load: "
        f"**{_format_force(uls.total_load)}**"
    )

    lines.append(
        f"- Left reaction: "
        f"**{_format_force(uls.left_reaction)}**"
    )

    lines.append(
        f"- Right reaction: "
        f"**{_format_force(uls.right_reaction)}**"
    )

    lines.append(
        f"- Maximum bending moment: "
        f"**{_format_moment(uls.max_bending_moment)}**"
    )

    lines.append(
        f"- Bending stress: "
        f"**{_format_stress(uls.bending_stress)}**"
    )

    lines.append("")

    lines.append("### ULS bending stress check")
    lines.append("")

    lines.append(
        f"- Calculated stress: "
        f"**{_format_stress(calculation.uls_stress_check.calculated_value)}**"
    )

    lines.append(
        f"- Allowable stress: "
        f"**{_format_stress(calculation.uls_stress_check.allowable_value)}**"
    )

    lines.append(
        f"- Utilisation: "
        f"**{calculation.uls_stress_check.utilisation:.3f}**"
    )

    lines.append(
        f"- Status: **{_check_status(calculation.uls_stress_check)}**"
    )

    lines.append("")

    # ==============================================================
    # 6. SLS
    # ==============================================================

    lines.append("## 6. Serviceability limit state")
    lines.append("")

    lines.append(
        f"- SLS distributed load: "
        f"**{_format_load(sls.distributed_load)}**"
    )

    lines.append(
        f"- Total SLS load: "
        f"**{_format_force(sls.total_load)}**"
    )

    lines.append(
        f"- Bending deflection: "
        f"**{_format_deflection(sls.bending_deflection)}**"
    )

    lines.append(
        f"- Shear deflection: "
        f"**{_format_deflection(sls.shear_deflection)}**"
    )

    lines.append(
        f"- Total deflection: "
        f"**{_format_deflection(sls.max_deflection)}**"
    )

    lines.append(
        f"- Shear contribution: "
        f"**{sls.shear_contribution:.2f}%**"
    )

    lines.append("")

    lines.append("### SLS deflection check")
    lines.append("")

    lines.append(
        f"- Calculated deflection: "
        f"**{_format_deflection(calculation.sls_deflection_check.calculated_value)}**"
    )

    lines.append(
        f"- Allowable deflection: "
        f"**{_format_deflection(calculation.sls_deflection_check.allowable_value)}**"
    )

    lines.append(
        f"- Utilisation: "
        f"**{calculation.sls_deflection_check.utilisation:.3f}**"
    )

    lines.append(
        f"- Status: **{_check_status(calculation.sls_deflection_check)}**"
    )

    lines.append("")

    # ==============================================================
    # 7. Overall result
    # ==============================================================

    lines.append("## 7. Overall result")
    lines.append("")

    lines.append(
        f"**Overall calculation status: "
        f"{calculation.status()}**"
    )

    lines.append("")

    lines.append(
        f"- ULS stress utilisation: "
        f"**{calculation.uls_stress_utilisation:.3f}**"
    )

    lines.append(
        f"- SLS deflection utilisation: "
        f"**{calculation.sls_deflection_utilisation:.3f}**"
    )

    lines.append(
        f"- Governing utilisation: "
        f"**{calculation.governing_utilisation():.3f}**"
    )

    lines.append(
        f"- Governing current check: "
        f"**{calculation.governing_check}**"
    )

    lines.append("")

    # ==============================================================
    # 8. Assumptions
    # ==============================================================

    lines.append("## 8. Engineering assumptions")
    lines.append("")

    if calculation.assumptions:
        for assumption in calculation.assumptions:
            lines.append(f"- {assumption}")
    else:
        lines.append("- No additional assumptions recorded.")

    lines.append("")

    # ==============================================================
    # 9. Warnings
    # ==============================================================

    lines.append("## 9. Warnings and limitations")
    lines.append("")

    if calculation.warnings:
        for warning in calculation.warnings:
            lines.append(f"- {warning}")
    else:
        lines.append("- No additional warnings recorded.")

    lines.append("")

    # ==============================================================
    # 10. Traceability
    # ==============================================================

    lines.append("## 10. Traceability")
    lines.append("")

    lines.append(
        "This calculation is generated from the GRP Structural Design "
        "Assistant calculation model."
    )

    lines.append("")

    lines.append(
        "The current prototype uses Euler-Bernoulli beam theory with "
        "orthotropic material-property inputs. Where shear deformation "
        "is enabled and suitable shear stiffness data are available, "
        "a Timoshenko shear contribution is included in the scalar "
        "deflection result."
    )

    lines.append("")

    lines.append(
        "The current calculation should not be interpreted as a complete "
        "Eurocode GRP member design. Items such as connection design, "
        "local buckling, instability, bearing, environmental reduction "
        "factors and detailed laminate/profile failure modes are outside "
        "the present calculation scope."
    )

    lines.append("")

    lines.append(
        f"*Report generated: "
        f"{datetime.now().isoformat(timespec='seconds')}*"
    )

    return "\n".join(lines)