import numpy as np
import pandas as pd
import streamlit as st

from Engineering.supports import SupportCondition
from Engineering.materials_library import available_materials
from Engineering.profiles import (
    rectangular_panel_section,
    evergrip_profile_catalog,
)
from Engineering.load_cases import calculate_self_weight_line_load
from Engineering.calculation_service import build_panel_calculation
from Engineering.calculation_report import generate_calculation_report
from Engineering.parameter_study import (
    run_span_study,
    span_study_dataframe,
    generate_span_values,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="GRP Structural Design Assistant",
    page_icon="🏗️",
    layout="wide",
)


# ============================================================
# HELPERS
# ============================================================

def format_number(value, decimals=2):
    if value is None:
        return "—"

    return f"{value:,.{decimals}f}"


def format_force(value):
    if value is None:
        return "—"

    if abs(value) >= 1000:
        return f"{value / 1000:,.2f} kN"

    return f"{value:,.1f} N"


def format_stress(value):
    if value is None:
        return "—"

    return f"{value / 1e6:,.2f} MPa"


def format_deflection(value):
    if value is None:
        return "—"

    return f"{value * 1000:,.2f} mm"


def format_utilisation(value):
    if value is None:
        return "—"

    return f"{value:.3f}"


def support_label(condition):
    value = getattr(condition, "value", str(condition))

    return value.replace("_", " ").title()


def get_profile_name(profile):
    return getattr(
        profile,
        "designation",
        getattr(profile, "name", "Custom section"),
    )


def get_profile_area(profile):
    return getattr(
        profile,
        "area",
        getattr(profile, "cross_sectional_area", None),
    )


def get_profile_second_moment(profile):
    return getattr(
        profile,
        "second_moment_of_area",
        getattr(profile, "second_moment_x", None),
    )


def get_profile_section_modulus(profile):
    return getattr(
        profile,
        "section_modulus",
        getattr(profile, "section_modulus_x", None),
    )


def get_profile_mass_per_length(profile):
    return getattr(
        profile,
        "mass_per_length",
        None,
    )


def get_material_density(material_record):
    return getattr(
        material_record,
        "density",
        None,
    )


def calculate_profile_self_weight(
    profile,
    material_record,
):
    """
    Calculate self-weight line load in N/m.

    Priority:
    1. Manufacturer profile mass per unit length.
    2. Material density × section area.
    3. Zero if neither is available.
    """

    try:
        line_load = calculate_self_weight_line_load(
            section=profile,
            material=material_record,
        )

        return float(line_load)

    except (TypeError, AttributeError):
        mass_per_length = get_profile_mass_per_length(profile)

        if mass_per_length is not None:
            return float(mass_per_length) * 9.81

        density = get_material_density(material_record)
        area = get_profile_area(profile)

        if density is not None and area is not None:
            return float(density) * float(area) * 9.81

        return 0.0


def get_catalogue_dataframe(profiles):
    rows = []

    for profile in profiles:
        rows.append(
            {
                "Designation": getattr(
                    profile,
                    "designation",
                    "—",
                ),
                "Type": getattr(
                    profile,
                    "section_type",
                    "—",
                ),
                "Area (mm²)": (
                    get_profile_area(profile) * 1e6
                    if get_profile_area(profile) is not None
                    else None
                ),
                "Ixx (mm⁴)": (
                    get_profile_second_moment(profile) * 1e12
                    if get_profile_second_moment(profile) is not None
                    else None
                ),
                "Mass (kg/m)": getattr(
                    profile,
                    "mass_per_length",
                    None,
                ),
            }
        )

    return pd.DataFrame(rows)


def get_diagram_dataframe(results):
    """
    Convert beam result arrays into a DataFrame suitable for
    Streamlit charts.
    """

    x = getattr(results, "x", None)
    shear = getattr(results, "shear", None)
    moment = getattr(results, "moment", None)
    deflection = getattr(results, "deflection", None)

    if x is None:
        return None

    data = {
        "x (m)": np.asarray(x),
    }

    if shear is not None:
        data["Shear force (N)"] = np.asarray(shear)

    if moment is not None:
        data["Bending moment (N·m)"] = np.asarray(moment)

    if deflection is not None:
        data["Bending deflection (m)"] = np.asarray(deflection)

    return pd.DataFrame(data)


# ============================================================
# HEADER
# ============================================================

st.title("GRP Structural Design Assistant")

st.markdown(
    """
    **Prototype engineering calculator for GRP/composite structural panels**

    The current model uses beam theory to assess a panel strip under
    uniformly distributed loading. Material and manufacturer properties
    are reference data and must be validated before engineering use.
    """
)

st.warning(
    "Prototype only — this tool is not a certified structural design "
    "package. Manufacturer data, design methodology, load factors and "
    "allowable values must be verified before engineering use."
)


# ============================================================
# MATERIAL SELECTION
# ============================================================

st.header("1. Material")

materials = available_materials()

if not materials:
    st.error("No materials are currently available.")
    st.stop()

material_names = list(materials.keys())

selected_material_name = st.selectbox(
    "Material / grade",
    material_names,
)

selected_material = materials[selected_material_name]
material = selected_material.get_material()


with st.expander("Material properties", expanded=True):

    material_col1, material_col2, material_col3 = st.columns(3)

    with material_col1:
        st.metric(
            "Axial modulus",
            f"{material.axial_youngs_modulus / 1e9:.2f} GPa",
        )

        st.metric(
            "Transverse modulus",
            f"{material.transverse_youngs_modulus / 1e9:.2f} GPa",
        )

        st.metric(
            "Shear modulus",
            (
                f"{material.shear_modulus / 1e9:.2f} GPa"
                if material.shear_modulus is not None
                else "Not available"
            ),
        )

    with material_col2:
        st.metric(
            "Allowable stress",
            f"{material.allowable_stress / 1e6:.1f} MPa",
        )

        density = get_material_density(selected_material)

        st.metric(
            "Density",
            (
                f"{density:,.0f} kg/m³"
                if density is not None
                else "Not available"
            ),
        )

        st.metric(
            "Poisson ratio",
            format_number(
                material.poisson_ratio,
                3,
            ),
        )

    with material_col3:
        st.write("**Manufacturer**")
        st.write(
            getattr(
                selected_material,
                "manufacturer",
                "—",
            )
        )

        st.write("**Product**")
        st.write(
            getattr(
                selected_material,
                "product",
                "—",
            )
        )

        st.write("**Standard grade**")
        st.write(
            getattr(
                selected_material,
                "standard_grade",
                "—",
            )
        )

    st.caption(
        getattr(
            selected_material,
            "validation_status",
            "Material validation status not specified.",
        )
    )


# ============================================================
# PROFILE SELECTION
# ============================================================

st.header("2. Structural profile")

profile_source = st.radio(
    "Profile source",
    [
        "Custom rectangular panel strip",
        "Evergrip manufacturer catalogue",
    ],
    horizontal=True,
)


selected_profile = None


# ------------------------------------------------------------
# CUSTOM RECTANGULAR PANEL
# ------------------------------------------------------------

if profile_source == "Custom rectangular panel strip":

    col1, col2 = st.columns(2)

    with col1:
        panel_width = st.number_input(
            "Panel strip width (mm)",
            min_value=1.0,
            value=100.0,
            step=10.0,
        )

    with col2:
        panel_thickness = st.number_input(
            "Panel thickness (mm)",
            min_value=1.0,
            value=10.0,
            step=1.0,
        )

    selected_profile = rectangular_panel_section(
        width=panel_width / 1000,
        thickness=panel_thickness / 1000,
    )

    st.info(
        "The custom panel is represented as a solid rectangular "
        "beam strip. This is a simplified model and should not be "
        "treated as a validated GRP sandwich or laminate model."
    )


# ------------------------------------------------------------
# EVERGRIP CATALOGUE
# ------------------------------------------------------------

else:

    catalogue_profiles = evergrip_profile_catalog()

    catalogue_df = get_catalogue_dataframe(
        catalogue_profiles
    )

    st.dataframe(
        catalogue_df,
        use_container_width=True,
        hide_index=True,
    )

    profile_designations = [
        getattr(
            profile,
            "designation",
            "Unknown",
        )
        for profile in catalogue_profiles
    ]

    selected_designation = st.selectbox(
        "Select catalogue profile",
        profile_designations,
    )

    selected_profile = next(
        profile
        for profile in catalogue_profiles
        if getattr(
            profile,
            "designation",
            None,
        ) == selected_designation
    )


# ============================================================
# SELECTED PROFILE PROPERTIES
# ============================================================

st.subheader("Selected profile")

profile_col1, profile_col2, profile_col3, profile_col4 = st.columns(4)

profile_area = get_profile_area(selected_profile)
profile_I = get_profile_second_moment(selected_profile)
profile_Z = get_profile_section_modulus(selected_profile)
profile_mass = get_profile_mass_per_length(selected_profile)

with profile_col1:
    st.metric(
        "Area",
        (
            f"{profile_area * 1e6:,.1f} mm²"
            if profile_area is not None
            else "—"
        ),
    )

with profile_col2:
    st.metric(
        "Ixx",
        (
            f"{profile_I * 1e12:,.0f} mm⁴"
            if profile_I is not None
            else "—"
        ),
    )

with profile_col3:
    st.metric(
        "Zxx",
        (
            f"{profile_Z * 1e9:,.2f} mm³"
            if profile_Z is not None
            else "Not available"
        ),
    )

with profile_col4:
    st.metric(
        "Mass",
        (
            f"{profile_mass:.2f} kg/m"
            if profile_mass is not None
            else "Calculated from density"
        ),
    )

if profile_Z is None:
    st.error(
        "The selected profile does not have a usable section modulus "
        "for the current bending stress calculation."
    )
    st.stop()

profile_status = getattr(
    selected_profile,
    "validation_status",
    None,
)

if profile_status:
    st.caption(profile_status)


# ============================================================
# STRUCTURAL INPUTS
# ============================================================

st.header("3. Structural inputs")

input_col1, input_col2, input_col3 = st.columns(3)

with input_col1:
    span = st.number_input(
        "Span (m)",
        min_value=0.10,
        value=2.00,
        step=0.10,
    )

with input_col2:
    tributary_width = st.number_input(
        "Tributary width (m)",
        min_value=0.01,
        value=0.50,
        step=0.05,
    )

with input_col3:
    support_options = list(SupportCondition)

    support_condition = st.selectbox(
        "Support condition",
        support_options,
        format_func=support_label,
    )


# ============================================================
# LOADS
# ============================================================

st.header("4. Loads")

st.write(
    "Enter additional characteristic area loads. "
    "Self-weight is calculated automatically where profile/material "
    "data permits."
)

load_col1, load_col2 = st.columns(2)

with load_col1:

    additional_permanent_load = st.number_input(
        "Additional permanent load Gk (kN/m²)",
        min_value=0.0,
        value=0.00,
        step=0.10,
    )

with load_col2:

    imposed_load = st.number_input(
        "Imposed / variable load Qk (kN/m²)",
        min_value=0.0,
        value=1.00,
        step=0.10,
    )


# ------------------------------------------------------------
# SELF WEIGHT
# ------------------------------------------------------------

self_weight_line = calculate_profile_self_weight(
    selected_profile,
    selected_material,
)

if tributary_width > 0:

    self_weight_area = (
        self_weight_line / tributary_width
    )

else:

    self_weight_area = 0.0


self_weight_area_kN = self_weight_area / 1000

permanent_load = (
    additional_permanent_load * 1000
    + self_weight_area
)

imposed_load_N = imposed_load * 1000

st.subheader("Characteristic load breakdown")

load_breakdown_col1, load_breakdown_col2, load_breakdown_col3 = st.columns(3)

with load_breakdown_col1:

    st.metric(
        "Self-weight",
        f"{self_weight_area_kN:.3f} kN/m²",
    )

with load_breakdown_col2:

    st.metric(
        "Additional permanent",
        f"{additional_permanent_load:.3f} kN/m²",
    )

with load_breakdown_col3:

    st.metric(
        "Total characteristic Gk",
        f"{permanent_load / 1000:.3f} kN/m²",
    )


# ============================================================
# LOAD FACTORS
# ============================================================

st.header("5. Load factors and design limits")

factor_col1, factor_col2, factor_col3 = st.columns(3)

with factor_col1:

    gamma_G = st.number_input(
        "γG",
        min_value=0.1,
        value=1.35,
        step=0.05,
    )

with factor_col2:

    gamma_Q = st.number_input(
        "γQ",
        min_value=0.1,
        value=1.50,
        step=0.05,
    )

with factor_col3:

    shear_correction_factor = st.number_input(
        "Shear correction factor",
        min_value=0.01,
        value=5 / 6,
        step=0.01,
        format="%.3f",
    )


limit_col1, limit_col2 = st.columns(2)

with limit_col1:

    allowable_stress_MPa = st.number_input(
        "Allowable bending stress (MPa)",
        min_value=0.1,
        value=float(
            material.allowable_stress / 1e6
        ),
        step=5.0,
    )

with limit_col2:

    deflection_limit_ratio = st.number_input(
        "Deflection limit ratio L /",
        min_value=50.0,
        value=250.0,
        step=10.0,
    )


allowable_stress = allowable_stress_MPa * 1e6

allowable_deflection = (
    span / deflection_limit_ratio
)


st.caption(
    f"Current allowable deflection = "
    f"{allowable_deflection * 1000:.2f} mm"
)


# ============================================================
# DESIGN CALCULATION
# ============================================================

st.header("6. Design calculation")

try:

    calculation = build_panel_calculation(
        span=span,
        tributary_width=tributary_width,
        permanent_load=permanent_load,
        imposed_load=imposed_load_N,
        gamma_G=gamma_G,
        gamma_Q=gamma_Q,
        support_condition=support_condition,
        material_record=selected_material,
        profile=selected_profile,
        allowable_stress=allowable_stress,
        allowable_deflection=allowable_deflection,
        shear_correction_factor=shear_correction_factor,
    )

except Exception as error:

    st.error(
        "The calculation could not be completed."
    )

    st.exception(error)

    st.stop()


# ============================================================
# DESIGN STATUS
# ============================================================

st.subheader("Design status")

if calculation.overall_pass:

    st.success(
        "PASS — the current prototype checks are within the "
        "specified limits."
    )

else:

    st.error(
        "FAIL — one or more prototype design checks exceed "
        "the specified limit."
    )


# ============================================================
# GOVERNING UTILISATION
# ============================================================

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

if uls_utilisation >= sls_utilisation:

    governing_criterion = "ULS bending stress"

else:

    governing_criterion = "SLS deflection"


util_col1, util_col2, util_col3 = st.columns(3)

with util_col1:

    st.metric(
        "ULS stress utilisation",
        format_utilisation(
            uls_utilisation
        ),
    )

with util_col2:

    st.metric(
        "SLS deflection utilisation",
        format_utilisation(
            sls_utilisation
        ),
    )

with util_col3:

    st.metric(
        "Governing utilisation",
        format_utilisation(
            governing_utilisation
        ),
    )


st.write(
    f"**Governing criterion:** {governing_criterion}"
)

st.caption(
    "Utilisation ≤ 1.000 represents a passing check."
)


# ============================================================
# LOAD CASE SUMMARY
# ============================================================

st.subheader("Load cases")

uls_area_load = (
    gamma_G * permanent_load
    + gamma_Q * imposed_load_N
)

sls_area_load = (
    permanent_load
    + imposed_load_N
)

uls_line_load = (
    uls_area_load * tributary_width
)

sls_line_load = (
    sls_area_load * tributary_width
)


load_case_col1, load_case_col2 = st.columns(2)

with load_case_col1:

    st.markdown("### ULS")

    st.write(
        f"Area load: **{uls_area_load / 1000:.3f} kN/m²**"
    )

    st.write(
        f"Line load: **{uls_line_load / 1000:.3f} kN/m**"
    )

with load_case_col2:

    st.markdown("### SLS")

    st.write(
        f"Area load: **{sls_area_load / 1000:.3f} kN/m²**"
    )

    st.write(
        f"Line load: **{sls_line_load / 1000:.3f} kN/m**"
    )


# ============================================================
# ULS RESULTS
# ============================================================

st.subheader("ULS results")

uls = calculation.uls_results

uls_col1, uls_col2, uls_col3, uls_col4 = st.columns(4)

with uls_col1:

    st.metric(
        "Left reaction",
        format_force(
            uls.left_reaction
        ),
    )

with uls_col2:

    st.metric(
        "Right reaction",
        format_force(
            uls.right_reaction
        ),
    )

with uls_col3:

    st.metric(
        "Maximum moment",
        format_force(
            uls.max_bending_moment
        ),
    )

with uls_col4:

    st.metric(
        "Bending stress",
        format_stress(
            uls.bending_stress
        ),
    )


uls_col5, uls_col6, uls_col7, uls_col8 = st.columns(4)

with uls_col5:

    st.metric(
        "Bending deflection",
        format_deflection(
            uls.bending_deflection
        ),
    )

with uls_col6:

    st.metric(
        "Shear deflection",
        format_deflection(
            uls.shear_deflection
        ),
    )

with uls_col7:

    st.metric(
        "Total deflection",
        format_deflection(
            uls.max_deflection
        ),
    )

with uls_col8:

    st.metric(
        "Shear contribution",
        f"{uls.shear_contribution:.2f}%",
    )


# ============================================================
# SLS RESULTS
# ============================================================

st.subheader("SLS results")

sls = calculation.sls_results

sls_col1, sls_col2, sls_col3, sls_col4 = st.columns(4)

with sls_col1:

    st.metric(
        "Left reaction",
        format_force(
            sls.left_reaction
        ),
    )

with sls_col2:

    st.metric(
        "Right reaction",
        format_force(
            sls.right_reaction
        ),
    )

with sls_col3:

    st.metric(
        "Maximum moment",
        format_force(
            sls.max_bending_moment
        ),
    )

with sls_col4:

    st.metric(
        "Maximum deflection",
        format_deflection(
            sls.max_deflection
        ),
    )


# ============================================================
# DESIGN CHECK TABLE
# ============================================================

st.subheader("Design checks")

check_dataframe = pd.DataFrame(
    [
        {
            "Check": "ULS bending stress",
            "Calculated": (
                f"{calculation.uls_stress_check.calculated_value / 1e6:.2f} MPa"
            ),
            "Allowable": (
                f"{calculation.uls_stress_check.allowable_value / 1e6:.2f} MPa"
            ),
            "Utilisation": (
                calculation.uls_stress_check.utilisation
            ),
            "Status": (
                "PASS"
                if calculation.uls_stress_check.passes
                else "FAIL"
            ),
        },
        {
            "Check": "SLS deflection",
            "Calculated": (
                f"{calculation.sls_deflection_check.calculated_value * 1000:.2f} mm"
            ),
            "Allowable": (
                f"{calculation.sls_deflection_check.allowable_value * 1000:.2f} mm"
            ),
            "Utilisation": (
                calculation.sls_deflection_check.utilisation
            ),
            "Status": (
                "PASS"
                if calculation.sls_deflection_check.passes
                else "FAIL"
            ),
        },
    ]
)

st.dataframe(
    check_dataframe,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# STRUCTURAL DIAGRAMS
# ============================================================

st.header("7. Structural diagrams")

diagram_df = get_diagram_dataframe(
    uls
)

if diagram_df is not None:

    tab1, tab2, tab3 = st.tabs(
        [
            "Shear force",
            "Bending moment",
            "Deflection",
        ]
    )

    with tab1:

        if "Shear force (N)" in diagram_df.columns:

            shear_chart = diagram_df[
                [
                    "x (m)",
                    "Shear force (N)",
                ]
            ].set_index("x (m)")

            st.line_chart(
                shear_chart,
                use_container_width=True,
            )

    with tab2:

        if "Bending moment (N·m)" in diagram_df.columns:

            moment_chart = diagram_df[
                [
                    "x (m)",
                    "Bending moment (N·m)",
                ]
            ].set_index("x (m)")

            st.line_chart(
                moment_chart,
                use_container_width=True,
            )

    with tab3:

        if "Bending deflection (m)" in diagram_df.columns:

            deflection_chart = diagram_df[
                [
                    "x (m)",
                    "Bending deflection (m)",
                ]
            ].set_index("x (m)")

            st.line_chart(
                deflection_chart,
                use_container_width=True,
            )

    st.caption(
        "The deflection diagram currently represents the "
        "Euler-Bernoulli bending component. Where Timoshenko "
        "shear deformation is available, its contribution is "
        "included in the reported scalar total deflection."
    )


# ============================================================
# PARAMETER STUDY
# ============================================================

st.header("8. Span parameter study")

st.write(
    "The parameter study repeats the complete ULS/SLS calculation "
    "for a range of spans using the current material, profile, "
    "loading and design limits."
)


study_col1, study_col2, study_col3 = st.columns(3)

with study_col1:

    default_min_span = max(
        0.50,
        span * 0.50,
    )

    study_min_span = st.number_input(
        "Minimum span (m)",
        min_value=0.10,
        value=float(
            round(default_min_span, 2)
        ),
        step=0.10,
        key="study_min_span",
    )


with study_col2:

    default_max_span = max(
        5.00,
        span * 1.50,
    )

    study_max_span = st.number_input(
        "Maximum span (m)",
        min_value=0.20,
        value=float(
            round(default_max_span, 2)
        ),
        step=0.10,
        key="study_max_span",
    )


with study_col3:

    study_points = st.number_input(
        "Number of points",
        min_value=2,
        max_value=100,
        value=20,
        step=1,
        key="study_points",
    )


if study_max_span <= study_min_span:

    st.error(
        "Maximum study span must be greater than "
        "minimum study span."
    )

else:

    try:

        spans = generate_span_values(
            minimum_span=study_min_span,
            maximum_span=study_max_span,
            number_of_points=int(
                study_points
            ),
        )

        study = run_span_study(
            spans=spans,
            tributary_width=tributary_width,
            permanent_load=permanent_load,
            imposed_load=imposed_load_N,
            gamma_G=gamma_G,
            gamma_Q=gamma_Q,
            support_condition=support_condition,
            material_record=selected_material,
            profile=selected_profile,
            allowable_stress=allowable_stress,
            allowable_deflection=(
                # The limit remains proportional to span,
                # therefore the parameter study must update it
                # for every span.
                1.0
            ),
            shear_correction_factor=(
                shear_correction_factor
            ),
        )

        study_df = span_study_dataframe(
            study
        )

        # ----------------------------------------------------
        # Correct SLS deflection utilisation for each span.
        #
        # The standard span study function uses one allowable
        # deflection value. For an L/ratio criterion the actual
        # allowable changes with span, so recalculate the SLS
        # utilisation consistently here.
        # ----------------------------------------------------

        corrected_sls_utilisation = []

        for i, study_span in enumerate(
            study.parameter_values
        ):

            allowable_at_span = (
                study_span
                / deflection_limit_ratio
            )

            calculation_at_span = build_panel_calculation(
                span=study_span,
                tributary_width=tributary_width,
                permanent_load=permanent_load,
                imposed_load=imposed_load_N,
                gamma_G=gamma_G,
                gamma_Q=gamma_Q,
                support_condition=support_condition,
                material_record=selected_material,
                profile=selected_profile,
                allowable_stress=allowable_stress,
                allowable_deflection=allowable_at_span,
                shear_correction_factor=(
                    shear_correction_factor
                ),
            )

            corrected_sls_utilisation.append(
                calculation_at_span
                .sls_deflection_check
                .utilisation
            )

        study_df[
            "SLS deflection utilisation"
        ] = corrected_sls_utilisation

        study_df[
            "Governing utilisation"
        ] = study_df[
            [
                "ULS stress utilisation",
                "SLS deflection utilisation",
            ]
        ].max(axis=1)

        study_df["Pass"] = (
            study_df["Governing utilisation"] <= 1.0
        )

        # ----------------------------------------------------
        # Table
        # ----------------------------------------------------

        display_df = study_df.copy()

        display_df[
            "ULS stress utilisation"
        ] = display_df[
            "ULS stress utilisation"
        ].round(3)

        display_df[
            "SLS deflection utilisation"
        ] = display_df[
            "SLS deflection utilisation"
        ].round(3)

        display_df[
            "Governing utilisation"
        ] = display_df[
            "Governing utilisation"
        ].round(3)

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # Utilisation chart
        # ----------------------------------------------------

        st.subheader(
            "Utilisation versus span"
        )

        chart_data = study_df[
            [
                "Span (m)",
                "ULS stress utilisation",
                "SLS deflection utilisation",
            ]
        ].set_index(
            "Span (m)"
        )

        st.line_chart(
            chart_data,
            use_container_width=True,
        )

        st.caption(
            "A utilisation of 1.0 represents the specified "
            "design limit. Values above 1.0 exceed that limit."
        )

        # ----------------------------------------------------
        # Governing span
        # ----------------------------------------------------

        max_index = (
            study_df[
                "Governing utilisation"
            ].idxmax()
        )

        max_row = study_df.loc[
            max_index
        ]

        st.write(
            f"**Highest utilisation in study:** "
            f"{max_row['Governing utilisation']:.3f} "
            f"at a span of "
            f"{max_row['Span (m)']:.2f} m."
        )

        # ----------------------------------------------------
        # First failing span
        # ----------------------------------------------------

        failing_rows = study_df[
            study_df["Governing utilisation"] > 1.0
        ]

        if not failing_rows.empty:

            first_failure = failing_rows.iloc[0]

            st.warning(
                f"The first span in the study exceeding "
                f"the utilisation limit is approximately "
                f"{first_failure['Span (m)']:.2f} m."
            )

        else:

            st.success(
                "No span in the selected study range "
                "exceeds the utilisation limit."
            )

    except Exception as error:

        st.error(
            "The span parameter study could not be completed."
        )

        st.exception(error)


# ============================================================
# ENGINEERING ASSUMPTIONS
# ============================================================

st.header("9. Engineering assumptions and limitations")

for assumption in calculation.assumptions:

    st.write(
        f"- {assumption}"
    )


if calculation.warnings:

    st.subheader("Warnings")

    for warning in calculation.warnings:

        st.warning(
            warning
        )


# ============================================================
# CALCULATION TRACEABILITY
# ============================================================

st.header("10. Calculation traceability")

trace_col1, trace_col2 = st.columns(2)

with trace_col1:

    st.markdown("### Material")

    st.write(
        f"**Name:** {calculation.inputs.material_name}"
    )

    st.write(
        f"**Manufacturer:** "
        f"{calculation.inputs.material_manufacturer}"
    )

    st.write(
        f"**Grade:** "
        f"{calculation.inputs.material_grade}"
    )

    st.write(
        f"**Validation:** "
        f"{calculation.inputs.material_validation_status}"
    )


with trace_col2:

    st.markdown("### Profile")

    st.write(
        f"**Profile:** "
        f"{calculation.inputs.profile_name}"
    )

    st.write(
        f"**Source:** "
        f"{calculation.inputs.profile_source}"
    )

    st.write(
        f"**Validation:** "
        f"{calculation.inputs.profile_validation_status}"
    )


# ============================================================
# CALCULATION SUMMARY
# ============================================================

st.subheader("Calculation summary")

summary_dataframe = pd.DataFrame(
    [
        {
            "Parameter": "Span",
            "Value": f"{span:.3f} m",
        },
        {
            "Parameter": "Tributary width",
            "Value": f"{tributary_width:.3f} m",
        },
        {
            "Parameter": "Support condition",
            "Value": support_label(
                support_condition
            ),
        },
        {
            "Parameter": "Permanent load Gk",
            "Value": (
                f"{permanent_load / 1000:.3f} kN/m²"
            ),
        },
        {
            "Parameter": "Imposed load Qk",
            "Value": (
                f"{imposed_load_N / 1000:.3f} kN/m²"
            ),
        },
        {
            "Parameter": "ULS area load",
            "Value": (
                f"{uls_area_load / 1000:.3f} kN/m²"
            ),
        },
        {
            "Parameter": "SLS area load",
            "Value": (
                f"{sls_area_load / 1000:.3f} kN/m²"
            ),
        },
        {
            "Parameter": "ULS maximum moment",
            "Value": format_force(
                uls.max_bending_moment
            ),
        },
        {
            "Parameter": "ULS bending stress",
            "Value": format_stress(
                uls.bending_stress
            ),
        },
        {
            "Parameter": "SLS maximum deflection",
            "Value": format_deflection(
                sls.max_deflection
            ),
        },
        {
            "Parameter": "Governing utilisation",
            "Value": (
                f"{governing_utilisation:.3f}"
            ),
        },
        {
            "Parameter": "Governing criterion",
            "Value": governing_criterion,
        },
        {
            "Parameter": "Overall status",
            "Value": calculation.status(),
        },
    ]
)

st.dataframe(
    summary_dataframe,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# REPORT
# ============================================================

st.header("11. Calculation report")

try:

    report_text = generate_calculation_report(
        calculation
    )

    st.download_button(
        label="Download calculation report",
        data=report_text,
        file_name="grp_structural_calculation_report.md",
        mime="text/markdown",
    )

    with st.expander(
        "Preview calculation report"
    ):

        st.markdown(
            report_text
        )

except Exception as error:

    st.error(
        "The calculation report could not be generated."
    )

    st.exception(error)


# ============================================================
# FUTURE DEVELOPMENT
# ============================================================

st.header("12. Future structural modules")

future_modules = [
    "Column compression checks",
    "Euler buckling",
    "Effective length factors",
    "Combined axial force and bending",
    "Local buckling of GRP profiles",
    "Connection and bolt checks",
    "Bearing and net-section checks",
    "Creep and long-term deflection",
    "Environmental reduction factors",
    "Automatic profile selection",
    "Automatic span/load optimisation",
    "Project save/load",
    "Professional calculation report export",
]

for module in future_modules:

    st.write(
        f"- {module}"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "GRP Structural Design Assistant — prototype engineering tool. "
    "Material and manufacturer properties require validation before "
    "engineering use."
)