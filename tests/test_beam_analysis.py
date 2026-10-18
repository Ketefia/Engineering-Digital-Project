import unittest

from Engineering.beam_analysis import (
    calculate_beam,
    calculate_beam_udl,
    calculate_beam_diagrams
)

from Engineering.load_cases import (
    analyse_point_load,
    analyse_udl
)

from Engineering.panel_analysis import (
    calculate_panel_udl
)

from Engineering.material import (
    Material
)

from Engineering.design_checks import (
    check_value
)

from Engineering.supports import SupportCondition

from Engineering.timoshenko import (
    calculate_shear_deflection_udl,
    calculate_shear_contribution
)

from Engineering.profiles import rectangular_panel_section

class TestBeamAnalysis(unittest.TestCase):

    def test_central_point_load(self):
        results = calculate_beam(
            span=2.0,
            load=2000.0,
            width=0.10,
            height=0.15,
            youngs_modulus=25e9
        )

        self.assertAlmostEqual(
            results.left_reaction,
            1000.0
        )

        self.assertAlmostEqual(
            results.right_reaction,
            1000.0
        )

        self.assertAlmostEqual(
            results.max_bending_moment,
            1000.0
        )

        expected_stress = (
            1000.0 / 0.000375
        )

        self.assertAlmostEqual(
            results.bending_stress,
            expected_stress
        )

    def test_negative_span_rejected(self):
        with self.assertRaises(ValueError):
            calculate_beam(
                span=-2.0,
                load=2000.0,
                width=0.10,
                height=0.15,
                youngs_modulus=25e9
            )

    def test_zero_height_rejected(self):
        with self.assertRaises(ValueError):
            calculate_beam(
                span=2.0,
                load=2000.0,
                width=0.10,
                height=0.0,
                youngs_modulus=25e9
            )

    def test_uniformly_distributed_load(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=25e9
        )

        results = calculate_beam_udl(
            span=2.0,
            distributed_load=1000.0,
            width=0.10,
            height=0.15,
            material=material
        )

        self.assertAlmostEqual(
            results.total_load,
            2000.0
        )

        self.assertAlmostEqual(
            results.left_reaction,
            1000.0
        )

        self.assertAlmostEqual(
            results.right_reaction,
            1000.0
        )

        self.assertAlmostEqual(
            results.max_bending_moment,
            500.0
        )

        expected_stress = (
            500.0 / 0.000375
        )

        self.assertAlmostEqual(
            results.bending_stress,
            expected_stress
        )

        second_moment_of_area = (
            0.10 * 0.15**3 / 12
        )

        expected_deflection = (
            5
            * 1000.0
            * 2.0**4
            / (
                384
                * 25e9
                * second_moment_of_area
            )
        )

        self.assertAlmostEqual(
            results.max_deflection,
            expected_deflection
        )

    def test_negative_udl_rejected(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=25e9
        )

        with self.assertRaises(ValueError):
            calculate_beam_udl(
                span=2.0,
                distributed_load=-1000.0,
                width=0.10,
                height=0.15,
                material=material
            )

    def test_point_load_interface(self):
        results = analyse_point_load(
            span=2.0,
            load=2000.0,
            width=0.10,
            height=0.15,
            youngs_modulus=25e9
        )

        self.assertIsNotNone(
            results
        )

    def test_udl_interface(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=25e9
        )

        results = analyse_udl(
            span=2.0,
            distributed_load=1000.0,
            width=0.10,
            height=0.15,
            material=material
        )

        self.assertIsNotNone(
            results
        )

    def test_panel_area_load_conversion(self):
        material = Material(
            "Generic GRP",
            25e9
        )

        section = rectangular_panel_section(
    width=1.0,
    thickness=0.15
)

        results = calculate_panel_udl(
    span=2.0,
    tributary_width=1.0,
    section=section,
    area_load=2000.0,
    material=material
)

        self.assertAlmostEqual(
            results.distributed_load,
            2000.0
        )

        self.assertAlmostEqual(
            results.total_load,
            4000.0
        )

        self.assertAlmostEqual(
            results.max_bending_moment,
            1000.0
        )

    def test_tributary_width_and_section_width_are_independent(self):
        material = Material(
            "Generic GRP",
            25e9
        )

        section = rectangular_panel_section(
    width=1.0,
    thickness=0.15
)

        results = calculate_panel_udl(
        span=2.0,
        tributary_width=1.5,
        section=section,
        area_load=2000.0,
        material=material
)

        self.assertAlmostEqual(
            results.distributed_load,
            3000.0
        )

        self.assertAlmostEqual(
            results.total_load,
            6000.0
        )

        self.assertAlmostEqual(
            results.max_bending_moment,
            1500.0
        )

    def test_design_check_passes(self):
        result = check_value(
            calculated_value=50.0,
            allowable_value=100.0
        )

        self.assertTrue(
            result.passes
        )

    def test_design_check_fails(self):
        result = check_value(
            calculated_value=150.0,
            allowable_value=100.0
        )

        self.assertFalse(
            result.passes
        )

    def test_design_check_zero_allowable_rejected(self):
        with self.assertRaises(ValueError):
            check_value(
                calculated_value=50.0,
                allowable_value=0.0
            )

    def test_beam_diagrams(self):
        results = calculate_beam_diagrams(
            span=2.0,
            distributed_load=2000.0
        )

        self.assertAlmostEqual(
            results["shear"][0],
            2000.0
        )

        self.assertAlmostEqual(
            results["shear"][50],
            0.0
        )

        self.assertAlmostEqual(
            results["moment"][50],
            1000.0
        )

        self.assertAlmostEqual(
            results["moment"][-1],
            0.0
        )

    def test_beam_udl_includes_diagram_data(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=25e9
        )

        results = calculate_beam_udl(
            span=2.0,
            distributed_load=2000.0,
            width=0.10,
            height=0.15,
            material=material
        )

        self.assertEqual(
            len(results.x),
            101
        )

        self.assertEqual(
            len(results.shear),
            101
        )

        self.assertEqual(
            len(results.moment),
            101
        )

        self.assertAlmostEqual(
            results.max_bending_moment,
            1000.0
        )

    def test_beam_udl_includes_deflection_data(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=25e9
        )

        results = calculate_beam_udl(
            span=2.0,
            distributed_load=2000.0,
            width=0.10,
            height=0.15,
            material=material
        )

        self.assertEqual(
            len(results.deflection),
            101
        )

        self.assertAlmostEqual(
            results.deflection[0],
            0.0
        )

        self.assertAlmostEqual(
            results.deflection[-1],
            0.0
        )

        self.assertGreater(
            abs(results.deflection[50]),
            0.0
        )

    def test_timoshenko_shear_deflection_udl(self):
        span = 2.0
        distributed_load = 2000.0
        shear_modulus = 5e9
        shear_area = 0.01
        shear_correction_factor = 5 / 6

        result = calculate_shear_deflection_udl(
            span=span,
            distributed_load=distributed_load,
            shear_modulus=shear_modulus,
            shear_area=shear_area,
            shear_correction_factor=shear_correction_factor
        )

        expected = (
            distributed_load
            * span**2
            / (
                8
                * shear_correction_factor
                * shear_area
                * shear_modulus
            )
        )

        self.assertAlmostEqual(
            result,
            expected
        )

    def test_udl_with_material(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=20e9,
            shear_modulus=3e9
        )

        result = calculate_beam_udl(
            span=2.0,
            distributed_load=1000.0,
            width=0.5,
            height=0.02,
            material=material
        )

        self.assertGreater(
            result.max_deflection,
            0
        )

        self.assertGreater(
            result.bending_stress,
            0
        )

    def test_fixed_fixed_udl_moment_diagram(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=25e9
        )

        results = calculate_beam_udl(
            span=2.0,
            distributed_load=1000.0,
            width=0.10,
            height=0.15,
            material=material,
            support_condition=SupportCondition.FIXED_FIXED
        )

        expected_support_moment = (
            -(1000.0 * 2.0**2) / 12.0
        )

        self.assertAlmostEqual(
            results.moment[0],
            expected_support_moment
        )

        self.assertAlmostEqual(
            results.moment[-1],
            expected_support_moment
        )
    def test_timoshenko_shear_contribution(self):
        bending_deflection = 0.010
        shear_deflection = 0.005

        contribution = calculate_shear_contribution(
            bending_deflection=bending_deflection,
            shear_deflection=shear_deflection
        )

        self.assertAlmostEqual(
            contribution,
            33.3333333333
        )

    def test_timoshenko_zero_deflection_contribution(self):
        contribution = calculate_shear_contribution(
            bending_deflection=0.0,
            shear_deflection=0.0
        )

        self.assertEqual(
            contribution,
            0.0
        )

if __name__ == "__main__":
    unittest.main()