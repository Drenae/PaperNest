import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from core.models.background_settings import (
    DEFAULT_BACKGROUND_COLOR,
    BackgroundMode,
    BackgroundSettings,
)
from services.settings.background import BackgroundService


class BackgroundServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.settings_path = self.root / "appearance.json"
        self.background_root = self.root / "backgrounds"
        self.service = BackgroundService(
            settings_path=self.settings_path,
            background_root=self.background_root,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def create_image(self, name: str = "source.png") -> Path:
        path = self.root / name
        Image.new("RGB", (24, 12), "#FFBF26").save(path)
        return path

    def test_load_uses_default_settings_when_file_is_absent(self) -> None:
        settings = self.service.load()

        self.assertEqual(settings.mode, BackgroundMode.IMAGE)
        self.assertEqual(settings.color, DEFAULT_BACKGROUND_COLOR)
        self.assertIsNone(settings.image_path)

    def test_use_color_normalizes_and_persists_the_value(self) -> None:
        settings = self.service.use_color("#aabbcc")

        self.assertEqual(settings.mode, BackgroundMode.COLOR)
        self.assertEqual(settings.color, "#AABBCC")
        self.assertEqual(self.service.load(), settings)

    def test_invalid_color_falls_back_to_default(self) -> None:
        settings = self.service.use_color("not-a-color")

        self.assertEqual(settings.color, DEFAULT_BACKGROUND_COLOR)

    def test_import_image_copies_it_and_does_not_keep_source_path(self) -> None:
        source = self.create_image()

        settings = self.service.import_image(source)

        imported = Path(settings.image_path or "")
        self.assertEqual(settings.mode, BackgroundMode.IMAGE)
        self.assertTrue(imported.is_file())
        self.assertEqual(imported.parent, self.background_root)
        self.assertNotEqual(imported, source)

    def test_import_image_rejects_a_fake_image(self) -> None:
        source = self.root / "fake.png"
        source.write_text("not an image", encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "image valide"):
            self.service.import_image(source)

    def test_missing_or_corrupt_image_falls_back_to_default(self) -> None:
        corrupt = self.background_root / "custom_background_corrupt.png"
        corrupt.parent.mkdir(parents=True)
        corrupt.write_text("broken", encoding="utf-8")
        self.settings_path.write_text(
            json.dumps(
                BackgroundSettings(image_path=str(corrupt)).to_dict()
            ),
            encoding="utf-8",
        )

        settings = self.service.load()

        self.assertIsNone(settings.image_path)

    def test_reset_removes_imported_images(self) -> None:
        settings = self.service.import_image(self.create_image())
        imported = Path(settings.image_path or "")

        reset_settings = self.service.reset()

        self.assertFalse(imported.exists())
        self.assertEqual(reset_settings, BackgroundSettings())


if __name__ == "__main__":
    unittest.main()
