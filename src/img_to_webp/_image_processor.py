import logging
import re
from pathlib import Path
from typing import List, Tuple, Optional

from PIL import Image

from ._exceptions import InputDirNotFoundError
from ._models import ImageSizeRule, ResizeMode

SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(
        self,
        input_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        overwrite: Optional[bool] = False,
        resize_mode: Optional[ResizeMode] = ResizeMode.CONTAIN,
        verbose: Optional[bool] = False,
        image_sizes: Optional[List[ImageSizeRule]] = None,
        default_size: Optional[Tuple[int, int]] = None,
        quality: Optional[int] = 80,
    ):
        self._input_dir = Path(input_dir) if input_dir else None
        self._output_dir = Path(output_dir) if output_dir else None
        self._overwrite = overwrite
        self._resize_mode = resize_mode
        self._verbose = verbose
        self._image_sizes = image_sizes or []
        self._default_size = default_size
        self._quality = quality

        log_level = logging.DEBUG if verbose else logging.INFO
        logging.getLogger().setLevel(log_level)

        self._total_images = 0
        self._processed_images = 0

    def process_all_images(self):
        """Processes all images in the input directory."""
        if not self._input_dir.exists():
            raise InputDirNotFoundError(self._input_dir)

        if not self._output_dir:
            logger.info("Output directory not specified, using input directory.")
            self._output_dir = self._input_dir

        self._output_dir.mkdir(parents=True, exist_ok=True)
        for image_path in self._input_dir.rglob("*"):
            if image_path.suffix.lower() in SUPPORTED_FORMATS:
                self.process_image(image_path)

        logger.info("Processing complete.")
        logger.info(f"Total images: {self._total_images}")
        logger.info(f"Processed images: {self._processed_images}")

    def process_image(self, img_path: Path):
        """Processes a single image file."""
        self._total_images += 1

        try:
            with Image.open(img_path) as img:
                img = img.convert("RGBA")

                size = (
                    self.get_size_from_filename(img_path.name)
                    or self._default_size
                    or img.size
                )

                img = self.resize_image(img, size)

                relative_path = img_path.relative_to(self._input_dir)
                output_path = self._output_dir / relative_path.with_suffix(".webp")
                output_path.parent.mkdir(parents=True, exist_ok=True)

                if not self._overwrite and output_path.exists():
                    logger.info(f"Skipping {img_path.name}: file already exists")
                    return

                img.save(output_path, "WEBP", quality=self._quality)
                self._processed_images += 1

                logger.info(f"Processed: {img_path.name} -> {output_path} ({size})")

        except (OSError, IOError) as e:
            logger.error(f"Skipping {img_path.name}: {e}")

    def get_size_from_filename(self, filename: str) -> Optional[Tuple[int, int]]:
        """Determines the size for an image based on regex patterns in image_sizes."""
        for file_size_rule in self._image_sizes:
            if re.match(file_size_rule.regex, filename):
                return tuple(file_size_rule.size)
        return None

    def resize_image(
        self,
        img: Image.Image,
        size: Tuple[int, int],
    ) -> Image.Image:
        """Resizes the image based on the selected mode."""
        if self._resize_mode == ResizeMode.COVER:
            return self.resize_cover(img, size)
        elif self._resize_mode == ResizeMode.CONTAIN:
            return self.resize_contain(img, size)
        elif self._resize_mode == ResizeMode.FILL:
            return self.resize_fill(img, size)
        elif self._resize_mode == ResizeMode.NONE:
            return img
        else:
            raise ValueError(f"Invalid resize mode: {self._resize_mode}")

    @staticmethod
    def resize_cover(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Resizes the image to completely cover the given size while maintaining aspect ratio."""
        if img.width * size[0] > img.height * size[1]:
            scale = size[1] / img.height
        else:
            scale = size[0] / img.width

        new_img_size = (int(img.width * scale), int(img.height * scale))
        new_img = img.resize(new_img_size, Image.Resampling.LANCZOS)

        left = int((new_img_size[0] - size[0]) / 2)
        top = int((new_img_size[1] - size[1]) / 2)
        right = int(left + size[0])
        bottom = int(top + size[1])

        return new_img.crop((left, top, right, bottom))

    @staticmethod
    def resize_contain(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Resizes the image to fit within the given size while maintaining aspect ratio."""
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img

    @staticmethod
    def resize_fill(img: Image.Image, size: Tuple[int, int]) -> Image.Image:
        """Resizes the image to fit within the given size while maintaining aspect ratio."""
        return img.resize(size, Image.Resampling.LANCZOS)
