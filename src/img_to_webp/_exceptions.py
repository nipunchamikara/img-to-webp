from pathlib import Path


class InputDirNotFoundError(RuntimeError):
    def __init__(self, input_dir: Path):
        super().__init__(f"Input directory not found: {input_dir}")


class ImageFileAlreadyExistsError(RuntimeError):
    def __init__(self, output_path: Path):
        super().__init__(f"Output file already exists: {output_path}")
