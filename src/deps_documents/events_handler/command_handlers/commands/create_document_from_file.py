from dataclasses import dataclass
from typing import Any

from deps_message_flow.commands.common import Command

__all__ = ["CreateDocumentFromFile", "CreateDocumentFromFileReply"]


@dataclass
class CreateDocumentFromFile(Command):
    document_name: str
    file_path: str
    document_type_id: str
    invoke_unifier: bool = True
    invoke_extraction: bool = True
    parsing_features: list[str] | None = None
    language: str | None = None
    engine: str | None = None
    llm_type: str | None = None
    group_id: str | None = None
    metadata: dict[str, Any] | None = None
    assigned_to_me: bool = False
    start_processing: bool = False


@dataclass
class CreateDocumentFromFileReply(Command):
    document_id: str | None = None
    error_type: str | None = None
    error_message: str | None = None
