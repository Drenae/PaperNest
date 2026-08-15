import json
import tempfile
import unittest
from pathlib import Path

from core.models.trash_settings import DEFAULT_TRASH_RETENTION_DAYS
from services.settings.trash import TrashSettingsService


class TrashSettingsServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.settings_path = Path(self.temporary_directory.name) / "trash_settings.json"
        self.service = TrashSettingsService(self.settings_path)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_load_uses_thirty_days_by_default(self) -> None:
        self.assertEqual(
            self.service.get_retention_days(),
            DEFAULT_TRASH_RETENTION_DAYS,
        )

    def test_save_persists_the_selected_duration(self) -> None:
        saved = self.service.save_retention_days("45")

        self.assertEqual(saved.retention_days, 45)
        self.assertEqual(self.service.get_retention_days(), 45)

    def test_save_rejects_non_numeric_or_out_of_range_values(self) -> None:
        for value in ("", "abc", "0", "3651"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.service.save_retention_days(value)

    def test_invalid_file_falls_back_to_default(self) -> None:
        self.settings_path.write_text(
            json.dumps({"retention_days": -10}),
            encoding="utf-8",
        )

        self.assertEqual(
            self.service.get_retention_days(),
            DEFAULT_TRASH_RETENTION_DAYS,
        )


if __name__ == "__main__":
    unittest.main()
