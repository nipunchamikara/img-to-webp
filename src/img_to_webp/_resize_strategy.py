from abc import ABC, abstractmethod

from PIL import Image

from ._models import ResizeMode


class ResizeStrategy(ABC):
    """Image resize strategy interface."""

    @abstractmethod
    def resize(self, img: Image, size: tuple[int, int]) -> Image:
        """Resizes an image to the specified size."""
        pass


class ResizeCoverStrategy(ResizeStrategy):
    def resize(self, img: Image, size: tuple[int, int]) -> Image:
        width, height = size
        if img.width * width > img.height * height:
            scale = height / img.height
        else:
            scale = width / img.width

        new_img_size = (int(img.width * scale), int(img.height * scale))
        new_img = img.resize(new_img_size, Image.Resampling.LANCZOS)

        left = int((new_img_size[0] - width) / 2)
        top = int((new_img_size[1] - height) / 2)
        right = int(left + width)
        bottom = int(top + height)

        return new_img.crop((left, top, right, bottom))


class ResizeContainStrategy(ResizeStrategy):
    def resize(self, img: Image, size: tuple[int, int]) -> Image:
        img.thumbnail(size, Image.Resampling.LANCZOS)
        return img


class ResizeFillStrategy(ResizeStrategy):
    def resize(self, img: Image, size: tuple[int, int]) -> Image:
        return img.resize(size, Image.Resampling.LANCZOS)


class ResizeNoneStrategy(ResizeStrategy):
    def resize(self, img: Image, size: tuple[int, int]) -> Image:
        return img


class ResizeStrategyFactory:
    @staticmethod
    def get_strategy(mode: ResizeMode) -> ResizeStrategy:
        if mode == ResizeMode.COVER:
            return ResizeCoverStrategy()
        elif mode == ResizeMode.CONTAIN:
            return ResizeContainStrategy()
        elif mode == ResizeMode.FILL:
            return ResizeFillStrategy()
        else:
            return ResizeNoneStrategy()


class ResizeStrategyFactoryProxy:
    def __init__(self):
        self._strategies = {}

    def get_strategy(self, mode: ResizeMode) -> ResizeStrategy:
        if mode not in self._strategies:
            self._strategies[mode] = ResizeStrategyFactory.get_strategy(mode)
        return self._strategies[mode]
