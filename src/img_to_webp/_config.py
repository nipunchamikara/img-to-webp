import argparse
import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import yaml

from ._models import ImageSizeRule, ResizeMode


@dataclass
class Config:
    input_dir: str
    output_dir: str
    overwrite: bool = False
    resize_mode: ResizeMode = ResizeMode.CONTAIN
    verbose: bool = False
    image_sizes: List[ImageSizeRule] = field(default_factory=list)
    default_size: Tuple[int, int] = (256, 256)
    quality: int = 80

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """Loads configuration from a YAML file."""
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        with open(yaml_path, "r") as file:
            config_dict = yaml.safe_load(file)

        image_sizes = [ImageSizeRule(**fs) for fs in config_dict.get("image_sizes", [])]

        input_dir = config_dict.get("input_dir", "")

        return cls(
            input_dir=input_dir,
            output_dir=config_dict.get("output_dir", input_dir),
            overwrite=config_dict.get("overwrite", False),
            resize_mode=config_dict.get("resize_mode", "contain"),
            verbose=config_dict.get("verbose", False),
            image_sizes=image_sizes,
            default_size=tuple(config_dict.get("default_size")) or (256, 256),
            quality=config_dict.get("quality", 80),
        )

    @classmethod
    def from_args(
        cls, args: argparse.Namespace, yaml_path: Optional[str] = None
    ) -> "Config":
        """Creates a config object by merging CLI args and YAML file settings."""
        yaml_config = cls.from_yaml(yaml_path) if yaml_path else None

        input_dir = args.input_dir or (yaml_config.input_dir if yaml_config else "")
        if not input_dir:
            raise ValueError("Input directory is required")

        return cls(
            input_dir=input_dir,
            output_dir=args.output_dir
            or (yaml_config.output_dir if yaml_config else input_dir),
            overwrite=(args.overwrite if args.overwrite is not None else False),
            resize_mode=ResizeMode(
                args.resize_mode
                or (yaml_config.resize_mode if yaml_config else "contain")
            ),
            verbose=(args.verbose if args.verbose is not None else False),
            image_sizes=yaml_config.image_sizes if yaml_config else [],
            default_size=yaml_config.default_size if yaml_config else (256, 256),
            quality=yaml_config.quality if yaml_config else 80,
        )
