import logging
import re
from pathlib import Path
from typing import List, Tuple, Optional

import PIL
from PIL import Image

from ._exceptions import InputDirNotFoundError, ImageFileAlreadyExistsError
from ._models import ResizeRule, ResizeMode
from ._resize_strategy import ResizeStrategyFactoryProxy, ResizeStrategy

SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(
        self,
        input_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        overwrite: Optional[bool] = False,
        default_resize_mode: Optional[ResizeMode] = ResizeMode.CONTAIN,
        verbose: Optional[bool] = False,
        resize_rules: Optional[List[ResizeRule]] = None,
        default_size: Optional[Tuple[int, int]] = None,
        quality: Optional[int] = 80,
    ):
        self._input_dir = Path(input_dir) if input_dir else None
        self._output_dir = Path(output_dir) if output_dir else None
        self._overwrite = overwrite
        self._default_resize_mode = default_resize_mode
        self._verbose = verbose
        self._resize_rules = resize_rules or []
        self._default_size = default_size
        self._quality = quality

        self._resize_strategy_factory = ResizeStrategyFactoryProxy()

        log_level = logging.DEBUG if verbose else logging.INFO
        logging.getLogger().setLevel(log_level)

    def process_all_images(self):
        """Processes all images in the input directory."""
        if not self._input_dir.exists():
            raise InputDirNotFoundError(self._input_dir)
        self._initialize_output_dir()

        [total_images, processed_images] = [0, 0]
        for image_path in self._input_dir.rglob("*"):
            if image_path.suffix.lower() in SUPPORTED_FORMATS:
                try:
                    total_images += 1
                    self.process_image(image_path)
                    processed_images += 1
                except (PIL.UnidentifiedImageError, ImageFileAlreadyExistsError) as e:
                    logger.error(f"Skipping {image_path.name}: {e}")

        logger.info("Processing complete.")
        logger.info(f"Total images: {total_images}")
        logger.info(f"Processed images: {processed_images}")

    def process_image(self, img_path: Path) -> Optional[Path]:
        """Processes a single image file."""

        with Image.open(img_path) as img:
            img = img.convert("RGBA")

            size, resize_mode = self._get_size_and_resize_mode(img_path.name)

            resize_strategy: ResizeStrategy = (
                self._resize_strategy_factory.get_strategy(resize_mode)
            )

            img = resize_strategy.resize(img, size)

            relative_path = img_path.relative_to(self._input_dir)
            output_path = self._output_dir / relative_path.with_suffix(".webp")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if not self._overwrite and output_path.exists():
                raise ImageFileAlreadyExistsError(output_path)

            img.save(output_path, "WEBP", quality=self._quality)
            logger.info(
                f"Processed: {img_path.name} -> {output_path} ({size}) ({resize_mode})"
            )
            return output_path

    def _get_size_and_resize_mode(
        self, filename: str
    ) -> Tuple[Optional[Tuple[int, int]], Optional[ResizeMode]]:
        """Determines the resize rule for an image based on pattern patterns in resize_rules."""
        for resize_rule in self._resize_rules:
            if re.match(resize_rule.pattern, filename):
                size = resize_rule.size or self._default_size
                mode = (
                    ResizeMode.NONE
                    if size is None
                    else (resize_rule.mode or self._default_resize_mode)
                )
                return size, mode
        mode = (
            ResizeMode.NONE if self._default_size is None else self._default_resize_mode
        )
        return self._default_size, mode

    def _initialize_output_dir(self):
        """Initializes the output directory."""
        if not self._output_dir:
            logger.info("Output directory not specified, using input directory.")
            self._output_dir = self._input_dir
        self._output_dir.mkdir(parents=True, exist_ok=True)
