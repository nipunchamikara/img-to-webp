import argparse
import unittest
from unittest.mock import patch, mock_open

from src.img_to_webp import Config, ResizeMode

yaml_data = """
input_dir: input
output_dir: output
resize_rule:
  - pattern: "*.jpg"
    size: [100, 100]
    mode: cover
quality: 90
default_size: [100, 100]
default_resize_mode: cover
overwrite: true
verbose: true
"""

args = argparse.Namespace(
    input_dir="input",
    output_dir="output",
    overwrite=True,
    default_resize_mode=ResizeMode.COVER,
    default_size=(100, 100),
    quality=90,
    verbose=True,
)


class TestConfig(unittest.TestCase):
    def assert_config(self, config):
        self.assertEqual(config.input_dir, "input")
        self.assertEqual(config.output_dir, "output")
        self.assertEqual(len(config.resize_rules), 1)
        self.assertEqual(config.resize_rules[0].pattern, "*.jpg")
        self.assertEqual(config.resize_rules[0].size, (100, 100))
        self.assertEqual(config.resize_rules[0].mode, ResizeMode.COVER)
        self.assertEqual(config.quality, 90)
        self.assertEqual(config.default_size, (100, 100))
        self.assertEqual(config.default_resize_mode, ResizeMode.COVER)
        self.assertTrue(config.overwrite)
        self.assertTrue(config.verbose)

    @patch("builtins.open", new_callable=mock_open, read_data=yaml_data)
    @patch("os.path.exists", return_value=True)
    def test_from_yaml(self, mock_exists, mock_file):
        config = Config.from_yaml("config.yaml")
        self.assert_config(config)

    @patch("argparse.Namespace", return_value=args)
    @patch("builtins.open", new_callable=mock_open, read_data=yaml_data)
    @patch("os.path.exists", return_value=True)
    def test_from_args(self, mock_exists, mock_file, mock_args):
        config = Config.from_args(mock_args(), "config.yaml")
        self.assert_config(config)

    def test_from_yaml_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            Config.from_yaml("config.yaml")

    @patch(
        "argparse.Namespace",
        return_value=argparse.Namespace(
            input_dir=None,
            **{key: value for key, value in vars(args).items() if key != "input_dir"},
        ),
    )
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="\n".join(yaml_data.split("\n")[2:]),
    )
    @patch("os.path.exists", return_value=True)
    def test_input_directory_required(self, mock_exists, mock_file, mock_args):
        with self.assertRaises(ValueError):
            Config.from_args(mock_args(), "config.yaml")


if __name__ == "__main__":
    unittest.main()
