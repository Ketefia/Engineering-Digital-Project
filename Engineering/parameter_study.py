from dataclasses import dataclass

import numpy as np
import pandas as pd

from Engineering.calculation_service import build_panel_calculation


@dataclass
class ParameterStudyResult:
    """
    Results from a structural parameter study.
    """

    parameter_name: str

    parameter_values: list[float]

    uls_stress_utilisation: list[float]

    sls_deflection_utilisation: list[float]

    governing_utilisation: list[float]

    passes: list[bool]


def generate_span_values(
    minimum_span,
    maximum_span,
    number_of_points=20,
):
    """
    Generate evenly spaced span values.

    Parameters
    ----------
    minimum_span : float
        Minimum span in metres.

    maximum_span : float
        Maximum span in metres.

    number_of_points : int
        Number of calculation points.

    Returns
    -------
    numpy.ndarray
    """

    if minimum_span <= 0:
        raise ValueError("Minimum span must be greater than zero.")

    if maximum_span <= minimum_span:
        raise ValueError(
            "Maximum span must be greater than minimum span."
        )

    if number_of_points < 2:
        raise ValueError(
            "Number of points must be at least 2."
        )

    return np.linspace(
        minimum_span,
        maximum_span,
        number_of_points,
    )


def run_span_study(
    spans,
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
    Run the complete panel calculation across a range of spans.

    The same:
        - material
        - profile
        - loads
        - support condition
        - design limits

    are retained while span is varied.
    """

    if allowable_deflection <= 0:
        raise ValueError(
            "Allowable deflection must be greater than zero."
        )

    parameter_values = []
    uls_utilisations = []
    sls_utilisations = []
    governing_utilisations = []
    passes = []

    for span in spans:

        calculation = build_panel_calculation(
            span=float(span),
            tributary_width=tributary_width,
            permanent_load=permanent_load,
            imposed_load=imposed_load,
            gamma_G=gamma_G,
            gamma_Q=gamma_Q,
            support_condition=support_condition,
            material_record=material_record,
            profile=profile,
            allowable_stress=allowable_stress,
            allowable_deflection=allowable_deflection,
            shear_correction_factor=shear_correction_factor,
        )

        uls_utilisation = (
            calculation.uls_stress_check.utilisation
        )

        sls_utilisation = (
            calculation.sls_deflection_check.utilisation
        )

        governing_utilisation = max(
            uls_utilisation,
            sls_utilisation,
        )

        parameter_values.append(float(span))
        uls_utilisations.append(uls_utilisation)
        sls_utilisations.append(sls_utilisation)
        governing_utilisations.append(governing_utilisation)
        passes.append(calculation.overall_pass)

    return ParameterStudyResult(
        parameter_name="Span",
        parameter_values=parameter_values,
        uls_stress_utilisation=uls_utilisations,
        sls_deflection_utilisation=sls_utilisations,
        governing_utilisation=governing_utilisations,
        passes=passes,
    )


def span_study_dataframe(result):
    """
    Convert span-study results into a pandas DataFrame.
    """

    return pd.DataFrame(
        {
            "Span (m)": result.parameter_values,
            "ULS stress utilisation":
                result.uls_stress_utilisation,
            "SLS deflection utilisation":
                result.sls_deflection_utilisation,
            "Governing utilisation":
                result.governing_utilisation,
            "Pass":
                result.passes,
        }
    )