# img-to-webp

[![Build and Test](https://github.com/nipunchamikara/img-to-webp/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/nipunchamikara/img-to-webp/actions/workflows/build-and-test.yml)

`img-to-webp` is a Python package that provides a command-line interface (CLI) for converting images to the WebP format.
It supports various image formats and allows for resizing images based on predefined rules.

## Features

- Convert images from various formats (PNG, JPG, JPEG, GIF, BMP, TIFF) to WebP.
- Resize images using different modes: `cover`, `contain`, `fill`, or `none`.
- Define custom resizing rules based on filename patterns.
- Option to overwrite existing files.
- Verbose logging for detailed processing information.

## Installation

To install the package for a user, you can use `pip`:

```sh
pip install -U img-to-webp
```

## Usage

### Command-Line Interface

You can use the CLI to process images by specifying the input and output directories, along with other options.

```sh
img-to-webp --input-dir INPUT_DIR [options]
```

### Options

- `--input-dir`: Directory containing the images to be processed.
- `--output-dir`: Directory where the processed images will be saved. If not specified, the output directory will be the
  same as the input directory.
- `--default-resize-mode`: Mode for resizing images (`cover`, `contain`, `fill`, `none`).
- `--default-size`: Default size for resizing images (width, height).
- `--quality`: Quality of the output WebP images (0-100).
- `--overwrite`: Overwrite existing files in the output directory.
- `--verbose`: Enable verbose logging.
- `--config`: Path to a YAML configuration file.

### Example

```sh
img-to-webp --input-dir ./images \
    --output-dir ./webp_images \
    --default-resize-mode cover \
    --default-size 256 256 \
    --quality 80 \
    --overwrite \
    --verbose
```

### Configuration File

You can also use a YAML configuration file to specify the settings. The CLI will merge the settings from the
configuration file with the command-line arguments.

```yaml
input_dir: ./images
output_dir: ./webp_images
default_resize_mode: cover
resize_rules:
  - pattern: ".*_small.*"
    size: [ 128, 128 ]
    mode: contain
  - pattern: ".*_large.*"
    size: [ 512, 512 ]
    mode: cover
default_size: [ 256, 256 ]
```

### Using Configuration File

```sh
img-to-webp --config config.yaml --overwrite
```

## Development

This project uses [uv](https://docs.astral.sh/uv/) Python package manager.
To set up the development environment, clone the repository and install the dependencies:

```sh
git clone https://github.com/nipunchamikara/img-to-webp.git
cd img-to-webp
uv venv
source .venv/bin/activate
uv sync --all-groups
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Contact

For any questions or issues, please open an issue on the GitHub repository.
