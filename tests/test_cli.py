import argparse
import unittest
from unittest.mock import patch

from src.img_to_webp import ResizeMode
from src.img_to_webp import parse_args


class TestCLI(unittest.TestCase):
    @patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(
            config="config.yaml",
            input_dir="input",
            output_dir="output",
            overwrite=True,
            default_resize_mode=ResizeMode.COVER,
            default_size=(100, 100),
            quality=90,
            verbose=True,
        ),
    )
    def test_parse_args(self, mock_args):
        args = parse_args()
        self.assertEqual(args.config, "config.yaml")
        self.assertEqual(args.input_dir, "input")
        self.assertEqual(args.output_dir, "output")
        self.assertTrue(args.overwrite)
        self.assertEqual(args.default_resize_mode, ResizeMode.COVER)
        self.assertEqual(args.default_size, (100, 100))
        self.assertEqual(args.quality, 90)
        self.assertTrue(args.verbose)


if __name__ == "__main__":
    unittest.main()
