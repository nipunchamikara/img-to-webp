from PIL import Image
from parameterized import parameterized

from src.img_to_webp import (
    ImageProcessor,
    InputDirNotFoundError,
    ResizeRule,
    ResizeMode,
    SUPPORTED_FORMATS,
)
from .base_test import BaseTest


class TestImageProcessor(BaseTest):
    def test_input_dir_not_found(self):
        processor = ImageProcessor(input_dir="tests/non_existent")
        with self.assertRaises(InputDirNotFoundError):
            processor.process_all_images()

    def test_output_dir_not_specified(self):
        processor = ImageProcessor(
            input_dir=str(self._input_dir),
        )

        processor.process_all_images()

        webp_files = list(self._input_dir.rglob("*.webp"))

        self.assertEqual(len(webp_files), len(SUPPORTED_FORMATS) * len(self.SIZES))

    def test_no_default_size(self):
        processor = ImageProcessor(
            input_dir=str(self._input_dir),
            output_dir=str(self._output_dir),
            overwrite=True,
        )
        img_list = self._input_dir.rglob("*")
        for image_path in img_list:
            img = Image.open(image_path)
            new_img = Image.open(processor.process_image(image_path))
            self.assertEqual(new_img.size, img.size)

    def test_no_pattern(self):
        processor = ImageProcessor(
            input_dir=str(self._input_dir),
            output_dir=str(self._output_dir),
            resize_rules=[],
            default_size=(100, 100),
            default_resize_mode=ResizeMode.COVER,
        )
        processor.process_all_images()

        webp_files = list(self._output_dir.rglob("*.webp"))
        for webp_file in webp_files:
            img = Image.open(webp_file)
            self.assertEqual(img.size, (100, 100))

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

    def test_invalid_image_file(self):
        processor = ImageProcessor(
            input_dir=str(self._input_dir),
        )
        invalid_file_name = "invalid_file.png"
        invalid_file_path = self._input_dir / invalid_file_name
        invalid_file_path.touch()
        with self.assertLogs() as cm:
            processor.process_all_images()
            self.assertIn(
                f"Skipping {invalid_file_name}: cannot identify image file",
                "\n".join(cm.output),
            )

    def test_image_size_pattern(self):
        crop_size = (50, 50)
        img_name_substr_1 = "test_image_100"
        img_name_substr_2 = "test_image_200"
        processor = ImageProcessor(
            input_dir=str(self._input_dir),
            resize_rules=[
                ResizeRule(img_name_substr_1, crop_size, str(ResizeMode.COVER))
            ],
            default_size=(100, 100),
        )
        processor.process_all_images()
        webp_files = list(self._output_dir.rglob(f"{img_name_substr_1}*.webp"))
        for webp_file in webp_files:
            img = Image.open(webp_file)
            new_size = self._calc_img_cover_size(img.size, crop_size)
            self.assertEqual(img.size, new_size)

        processor = ImageProcessor(
            input_dir=str(self._input_dir),
            resize_rules=[
                ResizeRule(img_name_substr_2, crop_size, str(ResizeMode.FILL))
            ],
            default_size=(100, 100),
        )
        processor.process_all_images()
        webp_files = list(self._output_dir.rglob(f"{img_name_substr_2}*.webp"))
        for webp_file in webp_files:
            img = Image.open(webp_file)
            self.assertEqual(img.size, crop_size)
