from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

from deps_documents.domain.constants import DocumentStateEnum, ErrorType

__all__ = ["UpdateDocumentState"]


@dataclass
class UpdateDocumentState(Command):
    document_id: str
    state: DocumentStateEnum
    error_type: Optional[ErrorType] = None
    error_message: Optional[str] = None
