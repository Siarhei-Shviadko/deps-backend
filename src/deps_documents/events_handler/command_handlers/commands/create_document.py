from dataclasses import dataclass
from typing import Any, Optional

from deps_message_flow.commands.common import Command

__all__ = ["CreateDocument", "CreateDocumentReply"]


@dataclass
class CreateDocument(Command):
    document_name: str
    document_type_id: str
    engine: str
    language: str
    llm_type: Optional[str]
    files: list[str]
    assign_to_me: bool
    document_metadata: Optional[dict[str, Any]] = None
    parent_id: Optional[str] = None


@dataclass
class CreateDocumentReply(Command):
    document_id: str
