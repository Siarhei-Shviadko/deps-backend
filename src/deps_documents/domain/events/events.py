import json
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional

from deps_message_flow.events.common import DomainEvent

from deps_documents.domain.constants import DocumentProcessingResult, DocumentStateEnum
from deps_documents.domain.entities.document_pk import DocumentEntityPk


@dataclass
class DocumentCreated(DomainEvent):
    document_id: DocumentEntityPk
    files: List[str]

    identify_document: bool
    extract_data: bool
    extract_attachments: bool
    extraction_params: Optional[Dict[str, Any]]

    document_type: Optional[str]
    engine: Optional[str]
    language: Optional[str]


@dataclass
class DocumentPreprocessBegan(DomainEvent):
    document_id: DocumentEntityPk


@dataclass
class DocumentPreprocessEnded(DomainEvent):
    document_id: DocumentEntityPk
    preprocess_result: List[Dict[str, Any]]

    identify_document: bool
    extract_data: bool
    extract_attachments: bool
    extraction_params: Optional[Dict[str, Any]]

    document_type: Optional[str]
    engine: Optional[str]
    language: Optional[str]


@dataclass
class ClassificationStarted(DomainEvent):
    document_id: DocumentEntityPk


@dataclass
class ClassificationEnded(DomainEvent):
    document_id: DocumentEntityPk
    document_type: Optional[str]
    classified_elements: List[Dict[str, Any]]

    engine: Optional[str]
    language: Optional[str]
    extraction_params: Optional[Dict[str, Any]]


@dataclass
class DocumentExtractionBegan(DomainEvent):
    document_id: DocumentEntityPk
    engine: str


@dataclass
class DocumentExtracted(DomainEvent):
    document_id: DocumentEntityPk


@dataclass
class DocumentDeleted(DomainEvent):
    document_id: DocumentEntityPk


@dataclass
class DocumentTypeChanged(DomainEvent):
    document_id: DocumentEntityPk


@dataclass
class DocumentImported(DomainEvent):
    document_name: str
    document_metadata: dict[str, Any]
    files_paths: List[str]
    document_type: str
    need_identification: bool = False


@dataclass
class DocumentProcessingSucceed(DomainEvent):
    document_id: DocumentEntityPk
    document_type: Optional[str] = None


@dataclass
class DocumentProcessingFailed(DomainEvent):
    document_id: DocumentEntityPk
    message: str


@dataclass
class DocumentValidationProcessingFailed(DomainEvent):
    document_id: DocumentEntityPk
    message: str


@dataclass
class DocumentExtractionDataFailed(DomainEvent):
    document_id: DocumentEntityPk
    message: str


@dataclass
class DocumentReviewCompleted(DomainEvent):
    document_id: DocumentEntityPk
    document_metadata: Dict[str, Any]


@dataclass
class UnknownDocumentType(DomainEvent):
    document_id: DocumentEntityPk


@dataclass
class OrganisationCreated(DomainEvent):
    id: str
    organisation_name: str
    personal: bool


@dataclass
class SampleDocumentsCreated(DomainEvent):
    documents: List[Dict[str, Any]]


@dataclass
class SampleDocumentsPreprocessed(DomainEvent):
    documents: List[Dict[str, Any]]


@dataclass
class DocumentUpdated(DomainEvent):
    document_id: DocumentEntityPk
    document: Dict[str, Any]
    metadata: Dict[str, Any]

    NON_SERIALIZABLE_FIELDS: ClassVar = ("date",)

    def __post_init__(self):
        for field in self.NON_SERIALIZABLE_FIELDS:
            value = self.document.get(field)
            if value is not None:
                self.document.update({field: json.dumps(value, default=str)})


@dataclass
class DocumentFieldsUpdated(DomainEvent):
    document_id: DocumentEntityPk
    document_metadata: Dict[str, Any]
    updates: Dict[str, Any]

    NON_SERIALIZABLE_FIELDS: ClassVar = ("date",)

    def __post_init__(self):
        for field in self.NON_SERIALIZABLE_FIELDS:
            value = self.updates.get(field)
            if value is not None:
                self.updates.update({field: json.dumps(value, default=str)})


@dataclass
class DocumentParsingBegan(DomainEvent):
    document_id: DocumentEntityPk


@dataclass
class DocumentParsingEnded(DomainEvent):
    document_id: DocumentEntityPk
    identify_document: bool
    extract_data: bool
    extraction_params: Dict[str, Any]
    document_type: Optional[str] = None
    engine: Optional[str] = None


@dataclass
class DocumentAssigned(DomainEvent):
    document_id: DocumentEntityPk
    user_id: str


@dataclass
class DocumentTypeCreated(DomainEvent):
    document_type: str
    tenant: str
    name: str


@dataclass
class DocumentTypeDeleted(DomainEvent):
    document_type: str
    tenant: str


@dataclass
class DocumentProcessed(DomainEvent):
    document_id: DocumentEntityPk
    document_type_code: str
    processing_result: DocumentProcessingResult
    error_message: Optional[str] = None


@dataclass
class DocumentClassificationCompleted(DomainEvent):
    document_id: str
    tenant_id: str
    document_type_id: Optional[str]


@dataclass
class GroupCreated(DomainEvent):
    id: str
    tenant_id: str
    name: str


@dataclass
class GroupDeleted(DomainEvent):
    id: str
    tenant_id: str


@dataclass
class GroupInfoUpdated(DomainEvent):
    id: str
    tenant_id: str
    name: str


@dataclass
class DocumentStateUpdated(DomainEvent):
    document_id: str
    state: str
    metadata: Dict[str, Any]
    error_in_state: Optional[DocumentStateEnum] = None


@dataclass
class DocumentTypeAssignedToDocument(DomainEvent):
    document_id: str
    document_type_id: str
    metadata: Dict[str, Any]
