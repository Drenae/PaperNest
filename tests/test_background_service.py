import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_apply_color_clears_decoration_and_sets_page_background(self) -> None:
        fake_flet = self.create_fake_flet()
        page = types.SimpleNamespace(bgcolor=None, decoration="previous")

        with patch.dict(sys.modules, {"flet": fake_flet}):
            self.service.apply(
                page,
                BackgroundSettings(mode=BackgroundMode.COLOR, color="#AABBCC"),
            )

        self.assertEqual(page.bgcolor, "#AABBCC")
        self.assertIsNone(page.decoration)

    def test_apply_image_uses_transparent_page_and_cropped_decoration(self) -> None:
        fake_flet = self.create_fake_flet()
        page = types.SimpleNamespace(bgcolor="#FFFFFF", decoration=None)

        with patch.dict(sys.modules, {"flet": fake_flet}):
            self.service.apply(
                page,
                BackgroundSettings(alignment_x=0.25, alignment_y=-0.5),
            )

        self.assertEqual(page.bgcolor, "transparent")
        self.assertEqual(
            page.decoration["image"]["src"],
            self.service.default_asset,
        )
        self.assertEqual(page.decoration["image"]["fit"], "cover")
        self.assertEqual(page.decoration["image"]["alignment"], (0.25, -0.5))

    def test_image_alignment_is_clamped_and_persisted(self) -> None:
        settings = self.service.import_image(
            self.create_image(),
            alignment_x=4,
            alignment_y=-3,
        )

        self.assertEqual(settings.alignment_x, 1.0)
        self.assertEqual(settings.alignment_y, -1.0)
        self.assertEqual(self.service.load(), settings)

    def test_zoom_crops_the_imported_image_to_the_requested_ratio(self) -> None:
        source = self.root / "wide.png"
        Image.new("RGB", (400, 200), "#FFBF26").save(source)

        settings = self.service.import_image(
            source,
            alignment_x=1.0,
            zoom=2.0,
            target_aspect_ratio=1.0,
        )

        with Image.open(Path(settings.image_path or "")) as imported:
            self.assertEqual(imported.size, (100, 100))
        self.assertEqual(settings.alignment_x, 0.0)
        self.assertEqual(settings.alignment_y, 0.0)

    def test_zoom_is_limited_to_four_times(self) -> None:
        source = self.root / "square.png"
        Image.new("RGB", (400, 400), "#FFBF26").save(source)

        settings = self.service.import_image(source, zoom=99, target_aspect_ratio=1.0)

        with Image.open(Path(settings.image_path or "")) as imported:
            self.assertEqual(imported.size, (100, 100))

    def test_zoom_out_extends_edges_without_black_bands(self) -> None:
        source = self.root / "portrait.png"
        image = Image.new("RGB", (100, 200), "#102030")
        image.paste("#FFBF26", (0, 0, 100, 1))
        image.paste("#D81B60", (0, 199, 100, 200))
        image.save(source)

        settings = self.service.import_image(
            source,
            zoom=0.5,
            target_aspect_ratio=1.0,
        )

        with Image.open(Path(settings.image_path or "")) as imported:
            self.assertEqual(imported.size, (200, 200))
            self.assertNotEqual(imported.getpixel((0, 100)), (0, 0, 0))
            self.assertNotEqual(imported.getpixel((199, 100)), (0, 0, 0))

    def test_zoom_out_is_limited_to_fifty_percent(self) -> None:
        source = self.root / "square-small.png"
        Image.new("RGB", (100, 100), "#FFBF26").save(source)

        settings = self.service.import_image(source, zoom=0.1, target_aspect_ratio=1.0)

        with Image.open(Path(settings.image_path or "")) as imported:
            self.assertEqual(imported.size, (200, 200))

    @staticmethod
    def create_fake_flet() -> types.SimpleNamespace:
        return types.SimpleNamespace(
            Colors=types.SimpleNamespace(TRANSPARENT="transparent"),
            BoxFit=types.SimpleNamespace(COVER="cover", CONTAIN="contain"),
            Alignment=lambda x, y: (x, y),
            DecorationImage=lambda **kwargs: kwargs,
            BoxDecoration=lambda **kwargs: kwargs,
        )


if __name__ == "__main__":
    unittest.main()
