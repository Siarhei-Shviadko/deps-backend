from dataclasses import dataclass
from typing import Optional

from deps_message_flow.commands.common import Command

from deps_documents.domain.entities import ParsingFeature

__all__ = ["ProcessDocument"]


@dataclass
class ProcessDocument(Command):
    document_id: str
    tenant_id: str
    files: list[str]
    document_type_id: Optional[str] = None
    engine: Optional[str] = None
    language: Optional[str] = None
    llm_type: Optional[str] = None
    parsing_features: Optional[list[ParsingFeature]] = None
    needs_unification: bool = True
    needs_extraction: bool = True
    needs_parsing: Optional[bool] = None
    needs_validation: Optional[bool] = None
    needs_review: Optional[str] = None
    needs_output_exporting: Optional[bool] = None
