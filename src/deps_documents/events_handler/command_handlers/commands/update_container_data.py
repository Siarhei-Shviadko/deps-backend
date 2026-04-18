from dataclasses import dataclass
from typing import Any, Optional

from deps_message_flow.commands.common import Command

__all__ = ["UpdateContainerData", "UpdateContainerDataReply"]


@dataclass
class UpdateContainerData(Command):
    document_id: str
    container_type: str
    container_metadata: dict[str, Any]


@dataclass
class UpdateContainerDataReply(Command):
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def has_error(self) -> bool:
        return self.error_type is not None
