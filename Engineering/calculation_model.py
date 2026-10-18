from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class CalculationInput:
    """
    Complete set of primary inputs required for a panel calculation.

    Units:
        span                m
        tributary_width     m
        permanent_load      N/m²
        imposed_load        N/m²
        gamma_G             -
        gamma_Q             -
    """

    span: float
    tributary_width: float

    permanent_load: float
    imposed_load: float

    gamma_G: float
    gamma_Q: float

    support_condition: str

    material_name: str
    material_manufacturer: str
    material_grade: str
    material_validation_status: str

    profile_name: str
    profile_source: str
    profile_validation_status: str


@dataclass
class CalculationSummary:
    """
    Structured record of a complete structural calculation.

    This object is intended to provide a single traceable representation
    of the calculation, independent of the Streamlit user interface.
    """

    inputs: CalculationInput

    uls_results: Any
    sls_results: Any

    uls_stress_check: Any
    sls_deflection_check: Any

    overall_pass: bool

    assumptions: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    calculation_id: str = field(default="")
    calculation_timestamp: str = field(default="")

    def __post_init__(self):
        if not self.calculation_id:
            self.calculation_id = self._generate_calculation_id()

        if not self.calculation_timestamp:
            self.calculation_timestamp = datetime.now().isoformat(
                timespec="seconds"
            )

    @staticmethod
    def _generate_calculation_id():
        """
        Generate a human-readable calculation identifier.

        Example:
            GRP-20260908-143215
        """
        return datetime.now().strftime("GRP-%Y%m%d-%H%M%S")

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self):
        """
        Return overall calculation status.
        """
        return "PASS" if self.overall_pass else "FAIL"

    # ------------------------------------------------------------------
    # Utilisation
    # ------------------------------------------------------------------

    def utilisation_summary(self):
        """
        Return the principal design utilisations.
        """
        return {
            "ULS stress utilisation": self.uls_stress_check.utilisation,
            "SLS deflection utilisation": self.sls_deflection_check.utilisation,
        }

    def governing_utilisation(self):
        """
        Return the largest utilisation from the current design checks.
        """
        return max(
            self.uls_stress_check.utilisation,
            self.sls_deflection_check.utilisation,
        )

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def uls_stress_utilisation(self):
        return self.uls_stress_check.utilisation

    @property
    def sls_deflection_utilisation(self):
        return self.sls_deflection_check.utilisation

    @property
    def governing_check(self):
        """
        Identify which current check has the larger utilisation.

        This is descriptive only; it does not alter the calculation.
        """
        if (
            self.uls_stress_check.utilisation
            >= self.sls_deflection_check.utilisation
        ):
            return "ULS bending stress"

        return "SLS deflection"

    # ------------------------------------------------------------------
    # Summary data
    # ------------------------------------------------------------------

    def summary_dict(self):
        """
        Return the principal calculation information as a dictionary.

        Useful for reports, exports and future API integration.
        """

        return {
            "calculation_id": self.calculation_id,
            "calculation_timestamp": self.calculation_timestamp,
            "status": self.status(),

            "material": self.inputs.material_name,
            "manufacturer": self.inputs.material_manufacturer,
            "material_grade": self.inputs.material_grade,

            "profile": self.inputs.profile_name,
            "profile_source": self.inputs.profile_source,

            "span_m": self.inputs.span,
            "tributary_width_m": self.inputs.tributary_width,

            "permanent_load_N_m2": self.inputs.permanent_load,
            "imposed_load_N_m2": self.inputs.imposed_load,

            "gamma_G": self.inputs.gamma_G,
            "gamma_Q": self.inputs.gamma_Q,

            "support_condition": self.inputs.support_condition,

            "ULS_stress_utilisation":
                self.uls_stress_check.utilisation,

            "SLS_deflection_utilisation":
                self.sls_deflection_check.utilisation,

            "governing_utilisation":
                self.governing_utilisation(),

            "governing_check":
                self.governing_check,
        }