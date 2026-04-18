from enum import Enum

__all__ = ["ParsingFeature"]


class ParsingFeature(str, Enum):
    TABLES = "tables"
    IMAGES = "images"
    KEY_VALUE_PAIRS = "kvps"
    TEXT = "text"
