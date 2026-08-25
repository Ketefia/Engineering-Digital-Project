from Engineering.beam_analysis import calculate_beam


# Design inputs
span = 2.0
load = 2000.0
width = 0.10
height = 0.15
youngs_modulus = 25e9


# Run engineering analysis
results = calculate_beam(
    span,
    load,
    width,
    height,
    youngs_modulus
)


# Display results
print("\nGRP ENGINEERING DESIGN ASSISTANT")
print("--------------------------------")

print(f"Span:                 {span:.2f} m")
print(f"Applied load:         {load:.0f} N")

print("\nSUPPORT REACTIONS")
print(f"Left reaction:        {results['left_reaction']:.2f} N")
print(f"Right reaction:       {results['right_reaction']:.2f} N")

print("\nSTRUCTURAL RESULTS")
print(
    f"Maximum moment:       "
    f"{results['max_bending_moment']:.2f} Nm"
)

print(
    f"Bending stress:       "
    f"{results['bending_stress'] / 1e6:.2f} MPa"
)

print(
    f"Maximum deflection:   "
    f"{results['max_deflection'] * 1000:.2f} mm"
)