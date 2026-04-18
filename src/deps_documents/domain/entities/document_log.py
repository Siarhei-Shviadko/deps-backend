from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from deps_documents.domain.constants import DocumentStateEnum


@dataclass
class StateInterval:
    state: DocumentStateEnum
    start_time: datetime
    finish_time: Optional[datetime]
