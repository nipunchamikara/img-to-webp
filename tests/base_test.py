import shutil
import unittest
from pathlib import Path
from typing import Any, Generator

from PIL import Image

from src.img_to_webp import SUPPORTED_FORMATS, ImageProcessor


class BaseTest(unittest.TestCase):
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

    def setUp(self):
        self._input_dir = Path("tests/input")
        self._output_dir = Path("tests/output")
        self._input_dir.mkdir(exist_ok=True)

        for fmt in SUPPORTED_FORMATS:
            for size in self.SIZES:
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

    @staticmethod
    def _calc_img_cover_size(
        old_size: tuple[int, int], new_size: tuple[int, int]
    ) -> tuple[int, int]:
        old_ratio = old_size[0] / old_size[1]
        new_ratio = new_size[0] / new_size[1]
        if old_ratio < new_ratio:
            scale = new_size[0] / old_size[0]
            return new_size[0], min(int(old_size[1] * scale), new_size[1])
        else:
            scale = new_size[1] / old_size[1]
            return min(int(old_size[0] * scale), new_size[0]), new_size[1]

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
