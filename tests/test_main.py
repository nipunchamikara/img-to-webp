import unittest
from unittest.mock import patch, MagicMock

from src.img_to_webp import main


class TestMain(unittest.TestCase):
    @patch("src.img_to_webp._main.ImageProcessor")
    @patch("src.img_to_webp._main.Config")
    @patch("src.img_to_webp._main.parse_args")
    def test_main(self, mock_parse_args, mock_config, mock_image_processor):
        mock_args = MagicMock()
        mock_args.config = "config.yaml"
        mock_parse_args.return_value = mock_args

        mock_config_instance = MagicMock()
        mock_config.from_args.return_value = mock_config_instance
        mock_config_instance.input_dir = "input"
        mock_config_instance.output_dir = "output"
        mock_config_instance.overwrite = True
        mock_config_instance.default_resize_mode = "cover"
        mock_config_instance.verbose = True
        mock_config_instance.resize_rules = []
        mock_config_instance.default_size = (100, 100)
        mock_config_instance.quality = 90

        mock_image_processor_instance = MagicMock()
        mock_image_processor.return_value = mock_image_processor_instance

        main()

        mock_parse_args.assert_called_once()
        mock_config.from_args.assert_called_once_with(mock_args, "config.yaml")
        mock_image_processor.assert_called_once_with(
            input_dir="input",
            output_dir="output",
            overwrite=True,
            default_resize_mode="cover",
            verbose=True,
            resize_rules=[],
            default_size=(100, 100),
            quality=90,
        )
        mock_image_processor_instance.process_all_images.assert_called_once()


if __name__ == "__main__":
    unittest.main()
