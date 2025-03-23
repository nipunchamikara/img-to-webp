from dataclasses import dataclass
from enum import Enum
from typing import Tuple


@dataclass
class ImageSizeRule:
    regex: str
    size: Tuple[int, int]


class ResizeMode(Enum):
    COVER = "cover"
    CONTAIN = "contain"
    FILL = "fill"
    NONE = "none"

    def __str__(self) -> str:
        return self.value
