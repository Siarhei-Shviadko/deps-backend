from dataclasses import dataclass
from typing import NewType, Optional

LabelEntityPk = NewType("LabelEntityPk", str)


@dataclass
class LabelEntity:
    name: str
    pk: Optional[LabelEntityPk] = None
