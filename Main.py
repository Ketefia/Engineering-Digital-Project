from Engineering.beam_analysis import (
    calculate_beam,
    calculate_beam_udl
)

from Engineering.panel_analysis import calculate_panel_udl

from Engineering.materials_library import (
    evergrip_e23_reference
)

from Engineering.profiles import (
    rectangular_panel_section
)


print("GRP ENGINEERING DESIGN ASSISTANT")
print("--------------------------------")


# ============================================================
# MATERIAL
# ============================================================

material_record = evergrip_e23_reference()
material = material_record.get_material()


print()
print("MATERIAL")
print("--------------------------------")
print(f"Material: {material.name}")
print(f"Manufacturer: {material_record.manufacturer}")
print(f"Product: {material_record.product}")
print(f"Grade: {material_record.standard_grade}")

print(
    f"Axial Young's modulus: "
    f"{material.axial_youngs_modulus / 1e9:.2f} GPa"
)

print(
    f"Transverse Young's modulus: "
    f"{material.transverse_youngs_modulus / 1e9:.2f} GPa"
)

if material.shear_modulus is not None:

    print(
        f"Shear modulus: "
        f"{material.shear_modulus / 1e9:.2f} GPa"
    )

else:

    print(
        "Shear modulus: Not available"
    )


# ============================================================
# POINT LOAD
# ============================================================

point_load_results = calculate_beam(
    span=2.0,
    point_load=2000.0,
    width=0.5,
    height=0.01,
    material=material
)

print()
print("POINT LOAD ANALYSIS")
print("--------------------------------")

print(
    f"Left reaction: "
    f"{point_load_results.left_reaction:.2f} N"
)

print(
    f"Right reaction: "
    f"{point_load_results.right_reaction:.2f} N"
)

print(
    f"Maximum moment: "
    f"{point_load_results.max_bending_moment:.2f} Nm"
)

print(
    f"Bending stress: "
    f"{point_load_results.bending_stress / 1e6:.2f} MPa"
)

print(
    f"Maximum deflection: "
    f"{point_load_results.max_deflection * 1000:.2f} mm"
)


# ============================================================
# UDL
# ============================================================

beam_results = calculate_beam_udl(
    span=2.0,
    distributed_load=1000.0,
    width=0.5,
    height=0.01,
    material=material
)

print()
print("UDL BEAM ANALYSIS")
print("--------------------------------")

print(
    f"Total load: "
    f"{beam_results.total_load:.2f} N"
)

print(
    f"Left reaction: "
    f"{beam_results.left_reaction:.2f} N"
)

print(
    f"Right reaction: "
    f"{beam_results.right_reaction:.2f} N"
)

print(
    f"Maximum moment: "
    f"{beam_results.max_bending_moment:.2f} Nm"
)

print(
    f"Bending stress: "
    f"{beam_results.bending_stress / 1e6:.2f} MPa"
)

print(
    f"Bending deflection: "
    f"{beam_results.bending_deflection * 1000:.2f} mm"
)

print(
    f"Shear deflection: "
    f"{beam_results.shear_deflection * 1000:.2f} mm"
)

print(
    f"Total deflection: "
    f"{beam_results.max_deflection * 1000:.2f} mm"
)

print(
    f"Shear contribution: "
    f"{beam_results.shear_contribution:.2f} %"
)


# ============================================================
# PANEL
# ============================================================

panel_section = rectangular_panel_section(
    width=0.5,
    thickness=0.01
)

panel_results = calculate_panel_udl(
    span=2.0,
    tributary_width=0.5,
    section=panel_section,
    area_load=2000.0,
    material=material
)

print()
print("PANEL UDL ANALYSIS")
print("--------------------------------")

print(
    f"Profile: "
    f"{panel_section.name}"
)

print(
    f"Area load: "
    f"{panel_results.area_load:.2f} N/m²"
)

print(
    f"Tributary width: "
    f"{panel_results.tributary_width:.2f} m"
)

print(
    f"Equivalent line load: "
    f"{panel_results.distributed_load:.2f} N/m"
)

print(
    f"Total load: "
    f"{panel_results.total_load:.2f} N"
)

print(
    f"Maximum moment: "
    f"{panel_results.max_bending_moment:.2f} Nm"
)

print(
    f"Bending stress: "
    f"{panel_results.bending_stress / 1e6:.2f} MPa"
)

print(
    f"Bending deflection: "
    f"{panel_results.bending_deflection * 1000:.2f} mm"
)

print(
    f"Shear deflection: "
    f"{panel_results.shear_deflection * 1000:.2f} mm"
)

print(
    f"Total deflection: "
    f"{panel_results.max_deflection * 1000:.2f} mm"
)

print(
    f"Shear contribution: "
    f"{panel_results.shear_contribution:.2f} %"
)