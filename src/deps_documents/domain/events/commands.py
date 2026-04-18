from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from deps_message_flow.commands.common import Command
from deps_message_flow.events.common import DomainEvent

from deps_documents.domain.entities.document_pk import DocumentEntityPk


@dataclass
class PreprocessDocument(DomainEvent):
    document_id: DocumentEntityPk
    files: List[str]

    identify_document: bool
    extract_data: bool
    extract_attachments: bool

    document_type: Optional[str]
    engine: Optional[str]
    language: Optional[str]


@dataclass
class ClassifyDocument(DomainEvent):
    document_id: DocumentEntityPk

    engine: Optional[str]
    language: Optional[str]
    extraction_params: Optional[Dict[str, Any]]


@dataclass
class ExtractData(DomainEvent):
    document_id: DocumentEntityPk
    language: Optional[str] = None
    engine: Optional[str] = None
    extraction_params: Optional[Dict[str, Any]] = None


@dataclass
class DeleteFiles(DomainEvent):
    file_paths: List[str]


@dataclass
class DeleteDocument(Command):
    document_id: DocumentEntityPk


@dataclass
class ValidationReply(Command):
    document_id: DocumentEntityPk
    is_valid: bool


@dataclass
class ImportDocument(Command):
    document_name: str
    document_metadata: dict[str, Any]
    file_path: str
    document_type: str
    invoke_unifier: bool = True
    invoke_extraction: bool = True
    parsing_features: Optional[list[str]] = None
    language: Optional[str] = None
    engine: Optional[str] = None
    llm_type: Optional[str] = None
    group_id: Optional[str] = None
    label_ids: Optional[list[str]] = None


@dataclass
class ImportDocumentReply(Command):
    document_id: DocumentEntityPk
    document_metadata: dict[str, Any]


class GetDocumentTypes(Command):
    pass  # noqa: WPS604, WPS420


@dataclass
class GetDocumentTypesReply(Command):
    document_types: list[dict[str, str]]


class GetGroups(Command):
    pass  # noqa: WPS604, WPS420


@dataclass
class GetGroupsReply(Command):
    groups: list[dict[str, Any]]
