import unittest

from Engineering.supports import SupportCondition


class TestSupportCondition(unittest.TestCase):

    def test_simply_supported_exists(self):
        self.assertEqual(
            SupportCondition.SIMPLY_SUPPORTED.value,
            "simply_supported"
        )


if __name__ == "__main__":
    unittest.main()