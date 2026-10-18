from dataclasses import dataclass


@dataclass
class Material:
    """
    Material definition for GRP/composite structural calculations.

    Units:
        Young's modulus: Pa
        Shear modulus: Pa
        Allowable stress: Pa
        Allowable deflection: m
        Poisson's ratios: dimensionless

    The material model supports orthotropic properties while retaining
    backward compatibility with the original Material API.

    IMPORTANT:
    Material properties are generic/reference values unless validated
    against the relevant manufacturer's technical documentation.
    """

    name: str

    # Primary / longitudinal Young's modulus
    youngs_modulus: float

    # Optional transverse Young's modulus
    transverse_youngs_modulus: float | None = None

    # Optional shear modulus
    shear_modulus: float | None = None

    # Optional allowable stress
    allowable_stress: float | None = None

    # Orthotropic Poisson ratios
    poisson_ratio_axial: float = 0.30
    poisson_ratio_transverse: float = 0.30

    # Optional serviceability limit
    allowable_deflection: float | None = None

    def __post_init__(self):
        # --------------------------------------------------------------
        # Young's modulus
        # --------------------------------------------------------------

        if self.youngs_modulus <= 0:
            raise ValueError(
                "Young's modulus must be greater than zero."
            )

        # --------------------------------------------------------------
        # Transverse Young's modulus
        # --------------------------------------------------------------

        if (
            self.transverse_youngs_modulus is not None
            and self.transverse_youngs_modulus <= 0
        ):
            raise ValueError(
                "Transverse Young's modulus must be greater than zero."
            )

        # --------------------------------------------------------------
        # Shear modulus
        # --------------------------------------------------------------

        if (
            self.shear_modulus is not None
            and self.shear_modulus <= 0
        ):
            raise ValueError(
                "Shear modulus must be greater than zero."
            )

        # --------------------------------------------------------------
        # Allowable stress
        # --------------------------------------------------------------

        if (
            self.allowable_stress is not None
            and self.allowable_stress <= 0
        ):
            raise ValueError(
                "Allowable stress must be greater than zero."
            )

        # --------------------------------------------------------------
        # Allowable deflection
        # --------------------------------------------------------------

        if (
            self.allowable_deflection is not None
            and self.allowable_deflection <= 0
        ):
            raise ValueError(
                "Allowable deflection must be greater than zero."
            )

        # --------------------------------------------------------------
        # Poisson ratios
        # --------------------------------------------------------------

        if not (-1.0 < self.poisson_ratio_axial < 0.5):
            raise ValueError(
                "Axial Poisson's ratio must be between -1 and 0.5."
            )

        if not (-1.0 < self.poisson_ratio_transverse < 0.5):
            raise ValueError(
                "Transverse Poisson's ratio must be between -1 and 0.5."
            )

    # ==================================================================
    # Young's modulus properties
    # ==================================================================

    @property
    def axial_youngs_modulus(self):
        """
        Young's modulus in the primary structural direction.
        """
        return self.youngs_modulus

    @property
    def transverse_modulus(self):
        """
        Alias for transverse Young's modulus.
        """
        return self.transverse_youngs_modulus

    # ==================================================================
    # Poisson ratio properties
    # ==================================================================

    @property
    def poisson_ratio(self):
        """
        Backward-compatible Poisson's ratio.

        The current beam calculations use the axial/primary value.
        """
        return self.poisson_ratio_axial

    @property
    def axial_poisson_ratio(self):
        """
        Descriptive alias for the axial Poisson ratio.
        """
        return self.poisson_ratio_axial

    @property
    def transverse_poisson_ratio(self):
        """
        Descriptive alias for the transverse Poisson ratio.
        """
        return self.poisson_ratio_transverse

    # ==================================================================
    # Material properties
    # ==================================================================

    def get_properties(self):
        """
        Return material properties for display, reporting and
        traceability.
        """

        return {
            "name": self.name,
            "axial_youngs_modulus": self.axial_youngs_modulus,
            "transverse_youngs_modulus":
                self.transverse_youngs_modulus,
            "shear_modulus": self.shear_modulus,
            "poisson_ratio_axial":
                self.poisson_ratio_axial,
            "poisson_ratio_transverse":
                self.poisson_ratio_transverse,
            "allowable_stress": self.allowable_stress,
            "allowable_deflection":
                self.allowable_deflection,
        }