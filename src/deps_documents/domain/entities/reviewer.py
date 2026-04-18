from dataclasses import dataclass
from typing import Optional


@dataclass
class Reviewer:
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
