from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class ResizeMode(Enum):
    COVER = "cover"
    CONTAIN = "contain"
    FILL = "fill"
    NONE = "none"

    def __str__(self) -> str:
        return self.value


@dataclass
class ResizeRule:
    pattern: str
    size: Tuple[int, int]
    mode: ResizeMode

    def __init__(self, pattern: str, size: Tuple[int, int], mode: str):
        self.pattern = pattern
        self.size = tuple(size)
        self.mode = ResizeMode(mode)
