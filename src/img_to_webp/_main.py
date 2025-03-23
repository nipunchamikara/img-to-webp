from ._cli import parse_args
from ._config import Config
from ._image_processor import ImageProcessor


def main():
    args = parse_args()
    config = Config.from_args(args, args.config)

    processor = ImageProcessor(
        input_dir=config.input_dir,
        output_dir=config.output_dir,
        overwrite=config.overwrite,
        resize_mode=config.resize_mode,
        verbose=config.verbose,
        image_sizes=config.image_sizes,
        default_size=config.default_size,
        quality=config.quality,
    )

    processor.process_all_images()


if __name__ == "__main__":
    main()
