import argparse
import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import yaml

from ._models import ResizeRule, ResizeMode


@dataclass
class Config:
    input_dir: str
    output_dir: str
    default_size: Optional[Tuple[int, int]] = None
    resize_rules: List[ResizeRule] = field(default_factory=list)
    default_resize_mode: ResizeMode = ResizeMode.CONTAIN
    quality: int = 80
    overwrite: bool = False
    verbose: bool = False

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "Config":
        """Loads configuration from a YAML file."""
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"Config file not found: {yaml_path}")

        with open(yaml_path, "r") as file:
            config_dict = yaml.safe_load(file)

        resize_rules = [ResizeRule(**fs) for fs in config_dict.get("resize_rules", [])]

        input_dir = config_dict.get("input_dir", "")

        return cls(
            input_dir=input_dir,
            output_dir=config_dict.get("output_dir", input_dir),
            resize_rules=resize_rules,
            quality=config_dict.get("quality", 80),
            default_size=tuple(config_dict.get("default_size")) or None,
            default_resize_mode=ResizeMode(
                config_dict.get("default_resize_mode", "contain")
            ),
            overwrite=config_dict.get("overwrite", False),
            verbose=config_dict.get("verbose", False),
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
            resize_rules=yaml_config.resize_rules if yaml_config else [],
            quality=args.quality or (yaml_config.quality if yaml_config else 80),
            default_size=tuple(args.default_size)
            if args.default_size is not None
            else (
                tuple(yaml_config.default_size)
                if yaml_config and yaml_config.default_size is not None
                else (256, 256)
            ),
            default_resize_mode=ResizeMode(
                args.default_resize_mode
                or (yaml_config.default_resize_mode if yaml_config else "contain")
            ),
            overwrite=args.overwrite,
            verbose=args.verbose,
        )
