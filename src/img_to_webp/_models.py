from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional


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
    size: Optional[Tuple[int, int]]
    mode: Optional[ResizeMode]

    def __init__(
        self,
        pattern: str,
        size: Optional[Tuple[int, int]] = None,
        mode: Optional[str] = None,
    ):
        if not mode and not size:
            raise ValueError("Either size or mode must be provided")

        self.pattern = pattern
        self.size = tuple(size) if size else None
        self.mode = ResizeMode(mode) if mode else None
