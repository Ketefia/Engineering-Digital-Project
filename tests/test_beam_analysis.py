import unittest

from Engineering.beam_analysis import (
    calculate_beam,
    calculate_beam_udl
)


class TestBeamAnalysis(unittest.TestCase):

    def test_central_point_load(self):
        results = calculate_beam(
            span=2.0,
            load=2000.0,
            width=0.10,
            height=0.15,
            youngs_modulus=25e9
        )

        # Support reactions
        self.assertAlmostEqual(
            results["left_reaction"],
            1000.0
        )

        self.assertAlmostEqual(
            results["right_reaction"],
            1000.0
        )

        # Maximum bending moment
        self.assertAlmostEqual(
            results["max_bending_moment"],
            1000.0
        )

        # Bending stress
        expected_stress = 1000.0 / 0.000375

        self.assertAlmostEqual(
            results["bending_stress"],
            expected_stress
        )
    def test_negative_span_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_beam(
                span=-2.0,
                load=2000.0,
                width=0.10,
                height=0.15,
                youngs_modulus=25e9
            )


    def test_zero_height_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_beam(
                span=2.0,
                load=2000.0,
                width=0.10,
                height=0.0,
                youngs_modulus=25e9
            )

    def test_uniformly_distributed_load(self):
         results = calculate_beam_udl(
            span=2.0,
            distributed_load=1000.0,
            width=0.10,
            height=0.15,
            youngs_modulus=25e9
        )

        # Total load = wL
         self.assertAlmostEqual(
            results["total_load"],
            2000.0
        )

        # Equal support reactions
         self.assertAlmostEqual(
            results["left_reaction"],
            1000.0
        )

         self.assertAlmostEqual(
            results["right_reaction"],
            1000.0
        )

        # Maximum bending moment = wL² / 8
         self.assertAlmostEqual(
            results["max_bending_moment"],
            500.0
        )

        # Bending stress = M / Z
         expected_stress = 500.0 / 0.000375

         self.assertAlmostEqual(
            results["bending_stress"],
            expected_stress
        )
        # Maximum deflection = 5wL^4 / 384EI
         expected_deflection = (
            5 * 1000.0 * 2.0**4
        ) / (
            384 * 25e9 * (0.10 * 0.15**3 / 12)
        )

         self.assertAlmostEqual(
            results["max_deflection"],
            expected_deflection
        )
    def test_negative_distributed_load_is_rejected(self):
        with self.assertRaises(ValueError):
            calculate_beam_udl(
                span=2.0,
                distributed_load=-1000.0,
                width=0.10,
                height=0.15,
                youngs_modulus=25e9
            )
            
if __name__ == "__main__":
    unittest.main()