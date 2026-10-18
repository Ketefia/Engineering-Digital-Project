from dataclasses import dataclass
from typing import Optional


# ============================================================
# GENERIC RECTANGULAR SECTION
# ============================================================

@dataclass(frozen=True)
class RectangularSection:
    width: float
    thickness: float

    def __post_init__(self):
        if self.width <= 0:
            raise ValueError("Width must be greater than zero.")

        if self.thickness <= 0:
            raise ValueError("Thickness must be greater than zero.")

    @property
    def name(self):
        return f"Rectangular panel strip {self.width:g} x {self.thickness:g} m"

    @property
    def area(self):
        return self.width * self.thickness

    @property
    def area_m2(self):
        return self.area

    @property
    def second_moment_of_area(self):
        return self.width * self.thickness**3 / 12.0

    @property
    def second_moment_of_area_x(self):
        return self.second_moment_of_area

    @property
    def second_moment_of_area_y(self):
        return self.thickness * self.width**3 / 12.0

    @property
    def section_modulus(self):
        return self.second_moment_of_area / (self.thickness / 2.0)

    @property
    def section_modulus_x(self):
        return self.section_modulus

    @property
    def section_modulus_y(self):
        return (
            self.second_moment_of_area_y
            / (self.width / 2.0)
        )

    @property
    def shear_area(self):
        return self.area

    @property
    def mass_per_length(self):
        return None

    @property
    def manufacturer(self):
        return "User-defined"

    @property
    def source(self):
        return "Calculated rectangular section"

    @property
    def validation_status(self):
        return "User-defined geometry"

    @property
    def section_modulus_source(self):
        return "Calculated from rectangular geometry"


def rectangular_panel_section(
    width: float,
    thickness: float,
) -> RectangularSection:

    return RectangularSection(
        width=width,
        thickness=thickness,
    )


# ============================================================
# MANUFACTURER PROFILE
# ============================================================

@dataclass(frozen=True)
class ManufacturerProfile:
    name: str
    section_type: str
    manufacturer: str
    source: str
    validation_status: str

    area: float
    second_moment_of_area_x: float

    second_moment_of_area_y: Optional[float] = None

    section_modulus_x: Optional[float] = None
    section_modulus_y: Optional[float] = None

    mass_per_length: Optional[float] = None

    dimensions: Optional[dict] = None

    section_modulus_source: str = (
        "Derived from catalogue geometry"
    )

    @property
    def area_m2(self):
        return self.area

    @property
    def second_moment_of_area(self):
        return self.second_moment_of_area_x

    @property
    def section_modulus(self):
        return self.section_modulus_x

    @property
    def shear_area(self):
        return self.area


# ============================================================
# EVERGRIP SOURCE INFORMATION
# ============================================================

SOURCE = (
    "Evergrip GRP Pultruded Sections - "
    "Technical Specification, April 2018"
)

VALIDATION = (
    "Catalogue data - validate against current "
    "manufacturer documentation before engineering use"
)

MANUFACTURER = "Evergrip Limited"

PRODUCT = "GRP Pultruded Sections"


# ============================================================
# SECTION MODULUS HELPERS
# ============================================================

def _z_from_height(
    ixx_mm4: float,
    height_mm: float,
) -> float:

    if height_mm <= 0:
        raise ValueError("Height must be greater than zero.")

    return (
        ixx_mm4 / (height_mm / 2.0)
    ) * 1e-9


def _z_round_tube(
    ixx_mm4: float,
    outer_diameter_mm: float,
) -> float:

    return _z_from_height(
        ixx_mm4,
        outer_diameter_mm,
    )


def _z_plate(
    ixx_mm4: float,
    thickness_mm: float,
) -> float:

    return _z_from_height(
        ixx_mm4,
        thickness_mm,
    )


def _equal_angle_centroid_from_outer_corner(
    width_mm: float,
    thickness_mm: float,
) -> float:

    b = width_mm
    t = thickness_mm

    area_geometry = (
        2.0 * b * t
        - t**2
    )

    first_moment = (
        (b * t) * (b / 2.0)
        + (t * b) * (t / 2.0)
        - (t * t) * (t / 2.0)
    )

    return first_moment / area_geometry


def _z_equal_angle(
    ixx_mm4: float,
    width_mm: float,
    thickness_mm: float,
) -> float:

    centroid = _equal_angle_centroid_from_outer_corner(
        width_mm,
        thickness_mm,
    )

    c_mm = width_mm - centroid

    return (
        ixx_mm4 / c_mm
    ) * 1e-9


# ============================================================
# PROFILE FACTORY
# ============================================================

def _profile(
    *,
    name,
    section_type,
    area_mm2,
    ixx_mm4,
    iyy_mm4=None,
    zxx_m3=None,
    zyy_m3=None,
    mass_kg_m=None,
    dimensions=None,
    section_modulus_source=(
        "Derived from catalogue geometry"
    ),
):

    return ManufacturerProfile(
        name=name,
        section_type=section_type,
        manufacturer=MANUFACTURER,
        source=SOURCE,
        validation_status=VALIDATION,
        area=area_mm2 * 1e-6,
        second_moment_of_area_x=ixx_mm4 * 1e-12,
        second_moment_of_area_y=(
            iyy_mm4 * 1e-12
            if iyy_mm4 is not None
            else None
        ),
        section_modulus_x=zxx_m3,
        section_modulus_y=zyy_m3,
        mass_per_length=mass_kg_m,
        dimensions=dimensions or {},
        section_modulus_source=section_modulus_source,
    )


# ============================================================
# EVERGRIP PROFILE CATALOGUE
# ============================================================

def evergrip_profile_catalog():

    profiles = []

    # ========================================================
    # ANGLES
    # ========================================================

    profiles.append(
        _profile(
            name="Angle 50 x 50 x 6",
            section_type="Angle",
            area_mm2=568,
            ixx_mm4=128_000,
            iyy_mm4=128_000,
            zxx_m3=_z_equal_angle(128_000, 50, 6),
            zyy_m3=_z_equal_angle(128_000, 50, 6),
            mass_kg_m=1.06,
            dimensions={
                "width_mm": 50,
                "height_mm": 50,
                "thickness_mm": 6,
            },
        )
    )

    profiles.append(
        _profile(
            name="Angle 60 x 60 x 8",
            section_type="Angle",
            area_mm2=910,
            ixx_mm4=296_000,
            iyy_mm4=296_000,
            zxx_m3=_z_equal_angle(296_000, 60, 8),
            zyy_m3=_z_equal_angle(296_000, 60, 8),
            mass_kg_m=1.69,
            dimensions={
                "width_mm": 60,
                "height_mm": 60,
                "thickness_mm": 8,
            },
        )
    )

    profiles.append(
        _profile(
            name="Angle 80 x 80 x 8",
            section_type="Angle",
            area_mm2=1236,
            ixx_mm4=736_000,
            iyy_mm4=736_000,
            zxx_m3=_z_equal_angle(736_000, 80, 8),
            zyy_m3=_z_equal_angle(736_000, 80, 8),
            mass_kg_m=2.30,
            dimensions={
                "width_mm": 80,
                "height_mm": 80,
                "thickness_mm": 8,
            },
        )
    )

    # ========================================================
    # SQUARE TUBES
    # ========================================================

    profiles.append(
        _profile(
            name="Square tube 50 x 50 x 5.95",
            section_type="Square tube",
            area_mm2=1048,
            ixx_mm4=340_000,
            iyy_mm4=340_000,
            zxx_m3=_z_from_height(340_000, 50),
            zyy_m3=_z_from_height(340_000, 50),
            mass_kg_m=2.20,
            dimensions={
                "width_mm": 50,
                "height_mm": 50,
                "wall_thickness_mm": 5.95,
            },
        )
    )

    profiles.append(
        _profile(
            name="Square tube 50.8 x 50.8 x 6.35",
            section_type="Square tube",
            area_mm2=1129,
            ixx_mm4=375_000,
            iyy_mm4=375_000,
            zxx_m3=_z_from_height(375_000, 50.8),
            zyy_m3=_z_from_height(375_000, 50.8),
            mass_kg_m=2.26,
            dimensions={
                "width_mm": 50.8,
                "height_mm": 50.8,
                "wall_thickness_mm": 6.35,
            },
        )
    )

    profiles.append(
        _profile(
            name="Square tube 75 x 75 x 6",
            section_type="Square tube",
            area_mm2=1668,
            ixx_mm4=1_334_000,
            iyy_mm4=1_334_000,
            zxx_m3=_z_from_height(1_334_000, 75),
            zyy_m3=_z_from_height(1_334_000, 75),
            mass_kg_m=3.27,
            dimensions={
                "width_mm": 75,
                "height_mm": 75,
                "wall_thickness_mm": 6,
            },
        )
    )

    profiles.append(
        _profile(
            name="Square tube 100 x 100 x 8",
            section_type="Square tube",
            area_mm2=2950,
            ixx_mm4=4_192_000,
            iyy_mm4=4_192_000,
            zxx_m3=_z_from_height(4_192_000, 100),
            zyy_m3=_z_from_height(4_192_000, 100),
            mass_kg_m=5.49,
            dimensions={
                "width_mm": 100,
                "height_mm": 100,
                "wall_thickness_mm": 8,
            },
        )
    )

    # ========================================================
    # CHANNELS
    # ========================================================

    profiles.append(
        _profile(
            name="Channel 120 x 50 x 6",
            section_type="Channel",
            area_mm2=1254,
            ixx_mm4=2_595_000,
            iyy_mm4=276_000,
            zxx_m3=_z_from_height(2_595_000, 120),
            mass_kg_m=2.32,
            dimensions={
                "height_mm": 120,
                "width_mm": 50,
                "thickness_mm": 6,
            },
        )
    )

    profiles.append(
        _profile(
            name="Channel 200 x 60 x 10",
            section_type="Channel",
            area_mm2=3005,
            ixx_mm4=15_729_000,
            iyy_mm4=820_500,
            zxx_m3=_z_from_height(15_729_000, 200),
            mass_kg_m=5.89,
            dimensions={
                "height_mm": 200,
                "width_mm": 60,
                "thickness_mm": 10,
            },
        )
    )

    profiles.append(
        _profile(
            name="Channel 240 x 72 x 12",
            section_type="Channel",
            area_mm2=4342,
            ixx_mm4=32_669_076,
            iyy_mm4=1_698_350,
            zxx_m3=_z_from_height(32_669_076, 240),
            mass_kg_m=8.47,
            dimensions={
                "height_mm": 240,
                "width_mm": 72,
                "thickness_mm": 12,
            },
        )
    )

    # ========================================================
    # I BEAMS
    # ========================================================

    profiles.append(
        _profile(
            name="I beam 60 x 120 x 6 x 6",
            section_type="I beam",
            area_mm2=1387,
            ixx_mm4=3_030_000,
            iyy_mm4=217_000,
            zxx_m3=_z_from_height(3_030_000, 120),
            mass_kg_m=2.57,
            dimensions={
                "width_mm": 60,
                "height_mm": 120,
                "web_thickness_mm": 6,
                "flange_thickness_mm": 6,
            },
        )
    )

    profiles.append(
        _profile(
            name="I beam 75 x 150 x 8 x 8",
            section_type="I beam",
            area_mm2=2292,
            ixx_mm4=7_745_000,
            iyy_mm4=566_000,
            zxx_m3=_z_from_height(7_745_000, 150),
            mass_kg_m=4.24,
            dimensions={
                "width_mm": 75,
                "height_mm": 150,
                "web_thickness_mm": 8,
                "flange_thickness_mm": 8,
            },
        )
    )

    profiles.append(
        _profile(
            name="I beam 100 x 200 x 10 x 10",
            section_type="I beam",
            area_mm2=3820,
            ixx_mm4=23_080_000,
            iyy_mm4=1_680_000,
            zxx_m3=_z_from_height(23_080_000, 200),
            mass_kg_m=7.07,
            dimensions={
                "width_mm": 100,
                "height_mm": 200,
                "web_thickness_mm": 10,
                "flange_thickness_mm": 10,
            },
        )
    )

    # ========================================================
    # ROUND TUBES
    # ========================================================

    profiles.append(
        _profile(
            name="Round tube 40 x 34 x 3",
            section_type="Round tube",
            area_mm2=350,
            ixx_mm4=60_000,
            zxx_m3=_z_round_tube(60_000, 40),
            mass_kg_m=0.65,
            dimensions={
                "outer_diameter_mm": 40,
                "inner_diameter_mm": 34,
                "wall_thickness_mm": 3,
            },
        )
    )

    profiles.append(
        _profile(
            name="Round tube 50 x 40 x 5",
            section_type="Round tube",
            area_mm2=707,
            ixx_mm4=181_000,
            zxx_m3=_z_round_tube(181_000, 50),
            mass_kg_m=1.32,
            dimensions={
                "outer_diameter_mm": 50,
                "inner_diameter_mm": 40,
                "wall_thickness_mm": 5,
            },
        )
    )

    # ========================================================
    # PLATES
    # ========================================================

    profiles.append(
        _profile(
            name="Plate 76 x 6.4",
            section_type="Plate",
            area_mm2=482,
            ixx_mm4=1_700,
            iyy_mm4=234_000,
            zxx_m3=_z_plate(1_700, 6.4),
            zyy_m3=_z_from_height(234_000, 76),
            mass_kg_m=0.89,
            dimensions={
                "width_mm": 76,
                "thickness_mm": 6.4,
            },
        )
    )

    profiles.append(
        _profile(
            name="Plate 228 x 12.5",
            section_type="Plate",
            area_mm2=2850,
            ixx_mm4=37_000,
            iyy_mm4=12_346_000,
            zxx_m3=_z_plate(37_000, 12.5),
            zyy_m3=_z_from_height(12_346_000, 228),
            mass_kg_m=5.41,
            dimensions={
                "width_mm": 228,
                "thickness_mm": 12.5,
            },
        )
    )

    return profiles


# ============================================================
# GROUPED CATALOGUE
# ============================================================

def available_manufacturer_profiles():

    profiles = evergrip_profile_catalog()

    result = {}

    for profile in profiles:

        section_type = profile.section_type

        if section_type not in result:
            result[section_type] = {}

        result[section_type][profile.name] = profile

    return result


# ============================================================
# FLAT PROFILE LOOKUP
# ============================================================

def manufacturer_profile_lookup():

    return {
        profile.name: profile
        for profile in evergrip_profile_catalog()
    }


def available_profile_names():

    return list(
        manufacturer_profile_lookup().keys()
    )


def available_profile_categories():

    return sorted(
        {
            profile.section_type
            for profile in evergrip_profile_catalog()
        }
    )


def get_manufacturer_profile(name):

    profiles = manufacturer_profile_lookup()

    if name not in profiles:
        raise ValueError(
            f"Unknown manufacturer profile: {name}"
        )

    return profiles[name]


# ============================================================
# API-FRIENDLY CATALOGUE
# ============================================================

def profile_catalog_for_api():

    profiles = evergrip_profile_catalog()

    output = []

    for profile in profiles:

        output.append(
            {
                "name": profile.name,
                "section_type": profile.section_type,
                "manufacturer": profile.manufacturer,
                "source": profile.source,
                "validation_status": profile.validation_status,

                "area_m2": profile.area_m2,

                "second_moment_of_area_x_m4":
                    profile.second_moment_of_area_x,

                "second_moment_of_area_y_m4":
                    profile.second_moment_of_area_y,

                "section_modulus_x_m3":
                    profile.section_modulus_x,

                "section_modulus_y_m3":
                    profile.section_modulus_y,

                "section_modulus_source":
                    profile.section_modulus_source,

                "mass_per_length_kg_m":
                    profile.mass_per_length,

                "dimensions":
                    profile.dimensions or {},
            }
        )

    return output


def profile_catalog_grouped_for_api():

    profiles = profile_catalog_for_api()

    grouped = {}

    for profile in profiles:

        section_type = profile["section_type"]

        if section_type not in grouped:
            grouped[section_type] = []

        grouped[section_type].append(profile)

    return grouped


# ============================================================
# BACKWARD-COMPATIBLE PROFILE API
# ============================================================

def available_profiles():

    return {
        "Rectangular panel strip":
            rectangular_panel_section,

        **available_manufacturer_profiles(),
    }