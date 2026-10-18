from dataclasses import dataclass

from Engineering.material import Material


@dataclass(frozen=True)
class MaterialRecord:
    """
    Manufacturer/material record containing the engineering material
    properties together with provenance information.

    All manufacturer/reference properties must be validated against
    the applicable technical documentation before engineering use.
    """

    material: Material

    manufacturer: str
    product: str
    standard_grade: str
    resin_system: str
    reinforcement: str

    source: str
    validation_status: str

    axial_tensile_strength: float | None = None
    transverse_tensile_strength: float | None = None

    axial_compressive_strength: float | None = None
    transverse_compressive_strength: float | None = None

    axial_flexural_strength: float | None = None
    transverse_flexural_strength: float | None = None

    interlaminar_shear_strength: float | None = None

    pin_bearing_strength_axial: float | None = None
    pin_bearing_strength_transverse: float | None = None

    density: float | None = None
    fibre_content_by_weight: float | None = None
    thermal_expansion_axial: float | None = None

    # ---------------------------------------------------------
    # Material access
    # ---------------------------------------------------------

    def get_material(self):
        return self.material

    # ---------------------------------------------------------
    # Convenience properties
    # ---------------------------------------------------------

    @property
    def name(self):
        return self.material.name

    @property
    def axial_youngs_modulus(self):
        return self.material.axial_youngs_modulus

    @property
    def youngs_modulus(self):
        """
        Backward-compatible alias for axial Young's modulus.
        """
        return self.material.axial_youngs_modulus

    @property
    def transverse_youngs_modulus(self):
        return self.material.transverse_youngs_modulus

    @property
    def shear_modulus(self):
        return self.material.shear_modulus

    @property
    def poisson_ratio(self):
        return self.material.poisson_ratio

    @property
    def allowable_stress(self):
        return self.material.allowable_stress

    # ---------------------------------------------------------
    # Material property dictionary
    # ---------------------------------------------------------

    def get_properties(self):
        return self.material.get_properties()


# =============================================================
# EVERGRIP E23 REFERENCE MATERIAL
# =============================================================

def evergrip_e23_reference():
    """
    Reference material record based on the supplied Evergrip
    technical specification.

    IMPORTANT:
    These values are reference data for the prototype and must
    be validated against current manufacturer documentation
    before engineering use.
    """

    material = Material(
        name="Evergrip E23 - reference data",

        # Published/reference effective flexural modulus.
        # This should not automatically be interpreted as a
        # generic isotropic Young's modulus.
        youngs_modulus=23e9,

        transverse_youngs_modulus=7e9,

        # No directly usable shear modulus was provided in the
        # supplied Evergrip technical specification.
        shear_modulus=None,

        allowable_stress=240e6,
    )

    return MaterialRecord(
        material=material,

        manufacturer="Evergrip Limited",

        product="GRP Pultruded Sections",

        standard_grade="EN 13706 E23",

        resin_system="Isophthalic polyester",

        reinforcement=(
            "E-glass fibre roving, woven fabric and filament mat"
        ),

        source=(
            "Evergrip GRP Pultruded Sections - "
            "Technical Specification, April 2018"
        ),

        validation_status=(
            "Reference data - validate before engineering use"
        ),

        axial_tensile_strength=240e6,

        transverse_tensile_strength=50e6,

        axial_compressive_strength=240e6,

        transverse_compressive_strength=70e6,

        axial_flexural_strength=240e6,

        transverse_flexural_strength=100e6,

        interlaminar_shear_strength=25e6,

        pin_bearing_strength_axial=150e6,

        pin_bearing_strength_transverse=70e6,

        density=1.72e3,

        fibre_content_by_weight=60.0,

        thermal_expansion_axial=8e-6,
    )


# =============================================================
# AVAILABLE MATERIALS
# =============================================================

def available_materials():
    """
    Return the available material records.

    IMPORTANT:
    The material factory functions are CALLED here so that the
    application receives MaterialRecord objects rather than
    function objects.
    """

    return {
        "Evergrip E23": evergrip_e23_reference(),
    }