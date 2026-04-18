from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

__all__ = ["AssignDocumentType", "AssignDocumentTypeReply"]


@dataclass
class AssignDocumentType(Command):
    document_id: str
    document_type_id: str


@dataclass
class AssignDocumentTypeReply(Command):
    error_type: Optional[str] = None
    error_message: Optional[str] = None

    @property
    def has_error(self) -> bool:
        return self.error_type is not None
