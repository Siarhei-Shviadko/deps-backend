from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

from deps_documents.domain.entities import ParsingFeature

__all__ = ["ClassifyDocument"]


@dataclass
class ClassifyDocument(Command):
    document_id: str
    tenant_id: str
    group_id: str
    files: list[str]
    engine: Optional[str] = None
    language: Optional[str] = None
    parsing_features: Optional[list[ParsingFeature]] = None
