import unittest
from decimal import Decimal

from services.documents.metadata import InvalidMetadataError, MetadataService


class MetadataAmountValidationTests(unittest.TestCase):
    def test_accepts_french_decimal_separator(self) -> None:
        self.assertEqual(
            MetadataService.validate_amount("145,50"),
            Decimal("145.50"),
        )

    def test_rejects_non_finite_amounts(self) -> None:
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value):
                with self.assertRaisesRegex(
                    InvalidMetadataError,
                    "montant saisi est invalide",
                ):
                    MetadataService.validate_amount(value)


if __name__ == "__main__":
    unittest.main()
