from PIL import Image

from src.img_to_webp import ResizeMode, ResizeStrategyFactory, ResizeStrategy
from .base_test import BaseTest


class TestResizeStrategies(BaseTest):
    def test_image_resize_cover(self):
        strategy = ResizeStrategyFactory.get_strategy(ResizeMode.COVER)
        for crop_size in self.CROP_SIZES:
            img_list = self._input_dir.rglob("*")
            for image_path in img_list:
                img = Image.open(image_path)
                new_size = self._calc_img_cover_size(img.size, crop_size)
                new_img = strategy.resize(img, crop_size)
                self.assertEqual(new_img.size, new_size)

    def test_image_resize_contain(self):
        strategy = ResizeStrategyFactory.get_strategy(ResizeMode.CONTAIN)
        for crop_size in self.CROP_SIZES:
            img_list = self._input_dir.rglob("*")
            for image_path in img_list:
                img = Image.open(image_path)
                ratio = min(crop_size[0] / img.width, crop_size[1] / img.height)
                expected_size = min(
                    (int(img.width * ratio), int(img.height * ratio)), img.size
                )

                new_img = strategy.resize(img, crop_size)
                for i in range(2):
                    self.assertAlmostEqual(new_img.size[i], expected_size[i], delta=1)

    def test_image_resize_fill(self):
        strategy = ResizeStrategyFactory.get_strategy(ResizeMode.FILL)
        for crop_size in self.CROP_SIZES:
            img_list = self._input_dir.rglob("*")
            for image_path in img_list:
                img = strategy.resize(Image.open(image_path), crop_size)
                self.assertEqual(img.size, crop_size)

    def test_image_resize_none(self):
        strategy = ResizeStrategyFactory.get_strategy(ResizeMode.NONE)
        img_list = self._input_dir.rglob("*")
        for image_path in img_list:
            img = Image.open(image_path)
            new_img = strategy.resize(img, (100, 100))
            self.assertEqual(new_img.size, img.size)

    def test_invalid_strategy(self):
        img = Image.new("RGB", (100, 100), color="white")
        with self.assertRaises(TypeError):
            ResizeStrategy().resize(img, (100, 100))
