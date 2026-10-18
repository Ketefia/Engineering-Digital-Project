import unittest

from Engineering.material import Material


class TestMaterial(unittest.TestCase):

    def test_material_creation(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=20e9,
            shear_modulus=3e9,
            allowable_stress=50e6,
            allowable_deflection=0.01
        )

        self.assertEqual(material.name, "Generic GRP")
        self.assertEqual(material.youngs_modulus, 20e9)
        self.assertEqual(material.shear_modulus, 3e9)
        self.assertEqual(material.allowable_stress, 50e6)
        self.assertEqual(material.allowable_deflection, 0.01)

    def test_invalid_youngs_modulus(self):
        with self.assertRaises(ValueError):
            Material(
                name="Generic GRP",
                youngs_modulus=0
            )

    def test_invalid_shear_modulus(self):
        with self.assertRaises(ValueError):
            Material(
                name="Generic GRP",
                youngs_modulus=20e9,
                shear_modulus=0
            )

    def test_invalid_allowable_stress(self):
        with self.assertRaises(ValueError):
            Material(
                name="Generic GRP",
                youngs_modulus=20e9,
                allowable_stress=0
            )

    def test_invalid_allowable_deflection(self):
        with self.assertRaises(ValueError):
            Material(
                name="Generic GRP",
                youngs_modulus=20e9,
                allowable_deflection=0
            )

    def test_material_without_optional_properties(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=20e9
        )

        self.assertIsNone(material.shear_modulus)
        self.assertIsNone(material.allowable_stress)
        self.assertIsNone(material.allowable_deflection)

    def test_evergrip_reference_material(self):
        material = Material(
            name="Evergrip E23 - reference data",
            youngs_modulus=23e9,
            allowable_stress=240e6
        )

        self.assertEqual(
            material.name,
            "Evergrip E23 - reference data"
        )

        self.assertEqual(
            material.youngs_modulus,
            23e9
        )

        self.assertEqual(
            material.allowable_stress,
            240e6
        )

    def test_orthotropic_material_properties(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=23e9,
            transverse_youngs_modulus=7e9,
            shear_modulus=3e9,
            poisson_ratio_axial=0.28,
            poisson_ratio_transverse=0.12
        )

        self.assertEqual(
            material.axial_youngs_modulus,
            23e9
        )

        self.assertEqual(
            material.youngs_modulus,
            23e9
        )

        self.assertEqual(
            material.transverse_youngs_modulus,
            7e9
        )

        self.assertEqual(
            material.shear_modulus,
            3e9
        )

        self.assertEqual(
            material.poisson_ratio_axial,
            0.28
        )

        self.assertEqual(
            material.poisson_ratio_transverse,
            0.12
        )

    def test_negative_transverse_modulus_rejected(self):
        with self.assertRaises(ValueError):
            Material(
                name="Invalid GRP",
                youngs_modulus=23e9,
                transverse_youngs_modulus=-7e9
            )

    def test_invalid_axial_poisson_ratio_rejected(self):
        with self.assertRaises(ValueError):
            Material(
                name="Invalid GRP",
                youngs_modulus=23e9,
                poisson_ratio_axial=0.6
            )

    def test_evergrip_e23_reference_library_material(self):
        from Engineering.materials_library import (
            evergrip_e23_reference
        )

        material = evergrip_e23_reference()

        self.assertEqual(
            material.name,
            "Evergrip E23 - reference data"
        )

        self.assertEqual(
            material.axial_youngs_modulus,
            23e9
        )

        self.assertEqual(
            material.transverse_youngs_modulus,
            7e9
        )

        self.assertIsNone(
            material.shear_modulus
        )

        self.assertEqual(
            material.allowable_stress,
            240e6
        )

    def test_get_properties(self):
        material = Material(
            name="Generic GRP",
            youngs_modulus=23e9,
            transverse_youngs_modulus=7e9,
            shear_modulus=3e9,
            poisson_ratio_axial=0.28,
            poisson_ratio_transverse=0.12,
            allowable_stress=240e6,
            allowable_deflection=0.01
        )

        properties = material.get_properties()

        self.assertEqual(
            properties["name"],
            "Generic GRP"
        )

        self.assertEqual(
            properties["axial_youngs_modulus"],
            23e9
        )

        self.assertEqual(
            properties["transverse_youngs_modulus"],
            7e9
        )

        self.assertEqual(
            properties["shear_modulus"],
            3e9
        )

        self.assertEqual(
            properties["poisson_ratio_axial"],
            0.28
        )

        self.assertEqual(
            properties["poisson_ratio_transverse"],
            0.12
        )

        self.assertEqual(
            properties["allowable_stress"],
            240e6
        )

        self.assertEqual(
            properties["allowable_deflection"],
            0.01
        )


if __name__ == "__main__":
    unittest.main()