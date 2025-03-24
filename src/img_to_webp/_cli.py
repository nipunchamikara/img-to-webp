import argparse

from ._models import ResizeMode


def parse_args():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Image processing CLI tool")

    parser.add_argument("--config", type=str, help="Path to config YAML file")
    parser.add_argument("--input-dir", type=str, help="Path to input directory")
    parser.add_argument("--output-dir", type=str, help="Path to output directory")
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing files"
    )
    parser.add_argument(
        "--default-resize-mode",
        type=ResizeMode,
        choices=list(ResizeMode),
        help="Resize mode",
    )
    parser.add_argument("--default-size", type=int, nargs=2, help="Default image size")
    parser.add_argument("--quality", type=int, help="WebP image quality")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    return parser.parse_args()
