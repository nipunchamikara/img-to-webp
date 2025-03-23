import shutil
import unittest
from pathlib import Path
from typing import Any, Generator

from PIL import Image
from parameterized import parameterized

from src.img_to_webp import (
    ImageProcessor,
    ResizeMode,
    SUPPORTED_FORMATS,
    InputDirNotFoundError,
)

SIZES = [(100, 200), (200, 100), (200, 200), (300, 200), (200, 300), (300, 300)]
CROP_SIZES = [
    (100, 200),
    (200, 100),
    (100, 100),
    (300, 200),
    (200, 300),
    (300, 300),
    (400, 200),
    (200, 400),
    (400, 400),
]


class TestImageProcessor(unittest.TestCase):
    def setUp(self):
        self._input_dir = Path("tests/input")
        self._output_dir = Path("tests/output")
        self._input_dir.mkdir(exist_ok=True)

        for fmt in SUPPORTED_FORMATS:
            for size in SIZES:
                img = Image.new("RGB", size, color="white")
                img.save(
                    self._input_dir
                    / f"test_image_{size[0]}x{size[1]}_{fmt.removeprefix('.')}{fmt}"
                )

    def tearDown(self):
        if self._input_dir.exists():
            shutil.rmtree(self._input_dir)
        if self._output_dir.exists():
            shutil.rmtree(self._output_dir)

    def test_input_dir_not_found(self):
        processor = ImageProcessor(
            input_dir="tests/non_existent",
            output_dir="tests/output",
            overwrite=True,
            resize_mode=ResizeMode.COVER,
            verbose=False,
            default_size=(256, 256),
            quality=80,
        )

        with self.assertRaises(InputDirNotFoundError):
            processor.process_all_images()

    def test_output_dir_not_specified(self):
        processor = ImageProcessor(
            input_dir=str(self._input_dir),
        )

        processor.process_all_images()

        webp_files = list(self._input_dir.rglob("*.webp"))

        self.assertEqual(len(webp_files), len(SUPPORTED_FORMATS) * len(SIZES))

    def test_image_resize_cover(self):
        for crop_size in CROP_SIZES:
            processor = ImageProcessor(
                resize_mode=ResizeMode.COVER,
                default_size=crop_size,
            )
            img_list = self._input_dir.rglob("*")
            for image_path in img_list:
                img = Image.open(image_path)
                img_ratio = img.width / img.height
                crop_ratio = crop_size[0] / crop_size[1]
                if img_ratio < crop_ratio:
                    scale = crop_size[0] / img.width
                    new_size = (
                        crop_size[0],
                        min(int(img.height * scale), crop_size[1]),
                    )
                else:
                    scale = crop_size[1] / img.height
                    new_size = (min(int(img.width * scale), crop_size[0]), crop_size[1])

                new_img = processor.resize_cover(img, crop_size)
                self.assertEqual(new_img.size, new_size)

    def test_image_resize_contain(self):
        for crop_size in CROP_SIZES:
            processor = ImageProcessor(
                resize_mode=ResizeMode.CONTAIN,
                default_size=crop_size,
            )
            img_list = self._input_dir.rglob("*")
            for image_path in img_list:
                img = Image.open(image_path)
                ratio = min(crop_size[0] / img.width, crop_size[1] / img.height)
                expected_size = min(
                    (int(img.width * ratio), int(img.height * ratio)), img.size
                )

                new_img = processor.resize_contain(img, crop_size)
                for i in range(2):
                    self.assertAlmostEqual(new_img.size[i], expected_size[i], delta=1)

    def test_image_resize_fill(self):
        for crop_size in CROP_SIZES:
            processor = ImageProcessor(
                resize_mode=ResizeMode.FILL,
                default_size=crop_size,
            )
            img_list = self._input_dir.rglob("*")
            for image_path in img_list:
                img = processor.resize_fill(Image.open(image_path), crop_size)
                self.assertEqual(img.size, crop_size)

    def test_image_resize_none(self):
        processor = ImageProcessor(
            resize_mode=ResizeMode.NONE,
            default_size=(256, 256),
        )
        img_list = self._input_dir.rglob("*")
        for image_path in img_list:
            img = Image.open(image_path)
            new_img = processor.resize_image(img, (100, 100))
            self.assertEqual(new_img.size, img.size)

    def test_no_default_size(self):
        processor = ImageProcessor(
            overwrite=True,
        )
        img_list = self._input_dir.rglob("*")
        for image_path in img_list:
            img = Image.open(image_path)
            new_img = processor.resize_image(img, (100, 100))
            self.assertEqual(new_img.size, img.size)

    def process_and_get_last_modified(
        self, iterations: int = 1, **kwargs: Any
    ) -> Generator[dict[Any, Any], Any, None]:
        for _ in range(iterations):
            processor = ImageProcessor(
                input_dir=str(self._input_dir),
                output_dir=str(self._output_dir),
                **kwargs,
            )

            processor.process_all_images()
            webp_files = list(self._output_dir.rglob("*.webp"))
            yield {f: f.stat().st_mtime for f in webp_files}

    @parameterized.expand([False, True])
    def test_image_overwrite_behavior(self, overwrite):
        [last_modified, new_last_modified] = self.process_and_get_last_modified(
            2,
            **{
                "overwrite": overwrite,
            },
        )
        if overwrite:
            self.assertNotEqual(last_modified, new_last_modified)
        else:
            self.assertEqual(last_modified, new_last_modified)


if __name__ == "__main__":
    unittest.main()
