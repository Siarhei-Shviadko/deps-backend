from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..constants import (
    DOCUMENT_ERROR_STATES,
    END_STATES,
    ActorEnum,
    ContainerTypesEnum,
    DocumentAssignmentStatusEnum,
    DocumentLogEnum,
    DocumentPriorityEnum,
    DocumentProcessingResult,
    DocumentStateEnum,
    ErrorType,
)
from ..domain_event import AggregateWithEvents
from ..events.events import DocumentAssigned, DocumentProcessed
from ..exceptions.document import DocumentAlreadyAssignedError, DocumentValidationError
from .document_pk import DocumentEntityPk
from .group import GroupEntity
from .label import LabelEntity
from .parsing_feature import ParsingFeature
from .relation import RelationEntity
from .reviewer import Reviewer


@dataclass
class BlobFileMetadata:
    width: int
    height: int


@dataclass
class BlobFile:
    blob_name: str
    metadata: Optional[BlobFileMetadata] = None


@dataclass
class ScrapedMetadataEntity:
    api_number: Optional[str] = None


@dataclass
class CommentEntity:
    text: str
    created_at: datetime
    created_by: Optional[str] = None


@dataclass
class CommunicationEntity:
    comments: List[CommentEntity] = field(default_factory=list)


@dataclass
class ErrorEntity:
    description: str = ""
    in_state: Optional[DocumentStateEnum] = None


@dataclass
class ContainerMetadata:
    first_level_child_count: int = None


@dataclass
class ContainerEmailMetadata(ContainerMetadata):
    subject: Optional[str] = None
    sender: Optional[str] = None
    recipients: List[str] = field(default_factory=list)
    cc: List[str] = field(default_factory=list)
    body: Optional[str] = None
    date: Optional[str] = None


class DocumentEntity(AggregateWithEvents):
    def __init__(
        self,  # pylint: disable=too-many-locals
        pk: DocumentEntityPk,
        title: str,
        state: DocumentStateEnum,
        files: List[BlobFile],
        date: datetime,
        document_type: Optional[str] = None,
        sub_type: Optional[str] = None,
        source_code: Optional[str] = None,
        reviewer: Optional[Reviewer] = None,
        labels: List[LabelEntity] = None,
        language: Optional[str] = None,
        engine: Optional[str] = None,
        llm_type: Optional[str] = None,
        parent_id: Optional[DocumentEntityPk] = None,
        group: Optional[GroupEntity] = None,
        container_type: Optional[ContainerTypesEnum] = None,
        container_metadata: Optional[ContainerEmailMetadata] = None,
        scraped_metadata: Optional[ScrapedMetadataEntity] = None,
        communication: Optional[CommunicationEntity] = None,
        preview_documents: List[BlobFile] = None,
        processing_documents: List[BlobFile] = None,
        error: Optional[ErrorEntity] = None,
        assigned_relations: List[RelationEntity] = None,
        assignment_status: Optional[DocumentAssignmentStatusEnum] = DocumentAssignmentStatusEnum.UNASSIGNED,
        priority: Optional[DocumentPriorityEnum] = DocumentPriorityEnum.LOW,
        extract_attachments: bool = True,
        parsing_features: Optional[set[ParsingFeature]] = None,
        needs_unification: bool = True,
        needs_extraction: bool = True,
        needs_parsing: Optional[bool] = None,
        needs_validation: Optional[bool] = None,
        needs_review: Optional[str] = None,
        needs_output_exporting: Optional[bool] = None,
    ):
        super().__init__()
        self.pk = pk
        self.title = title
        self._state = state
        self.assignment_status = assignment_status
        self.priority = priority
        self.files = files
        self.date = date
        self._document_type = document_type
        self.sub_type = sub_type
        self.source_code = source_code
        self._reviewer = reviewer
        self.labels = labels or []
        self.language = language
        self.engine = engine
        self.llm_type = llm_type
        self.parent_id = parent_id
        self.group = group
        self.container_type = container_type
        self.container_metadata = container_metadata
        self.scraped_metadata = scraped_metadata
        self.communication = communication
        self.preview_documents = preview_documents or []
        self.processing_documents = processing_documents or []
        self.error = error
        self.assigned_relations = assigned_relations if assigned_relations is not None else []
        self.extract_attachments = extract_attachments
        self.parsing_features = parsing_features
        self.needs_unification = needs_unification
        self.needs_extraction = needs_extraction
        self.needs_parsing = (
            needs_parsing or bool(parsing_features) if needs_parsing is None else needs_parsing and bool(parsing_features)
        )
        self.needs_validation = needs_validation
        self.needs_review = needs_review
        self.needs_output_exporting = needs_output_exporting

    def __eq__(self, other: object):
        if not isinstance(other, DocumentEntity):
            raise NotImplementedError

        return self.asdict() == other.asdict()

    def __repr__(self):
        return f"{self.__class__.__name__}{self.asdict()}"

    @property
    def blob_names(self) -> list[str]:
        return [file.blob_name for file in self.files]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if state == DocumentStateEnum.VALIDATION:
            self._check_validation_availability()
        self._state = state

    @property
    def reviewer(self):
        return self._reviewer

    @reviewer.setter
    def reviewer(self, reviewer):
        self._reviewer = reviewer

    def assign_reviewer(self, reviewer: Reviewer) -> None:
        if self._reviewer is None:
            self.add_event(DocumentAssigned(document_id=self.pk, user_id=reviewer.id))
        elif self._reviewer.id != reviewer.id:
            raise DocumentAlreadyAssignedError(doc_ids=[self.pk])
        self._reviewer = reviewer

    def unassign_reviewer(self) -> None:
        self._reviewer = None

    @property
    def document_type(self):
        return self._document_type

    @document_type.setter
    def document_type(self, document_type):
        self._document_type = document_type

    @property
    def group_id(self) -> Optional[str]:
        return self.group.id if self.group is not None else None

    def update_state(
        self,
        state: DocumentStateEnum,
        error_type: Optional[ErrorType] = None,
        error_message: Optional[str] = None,
    ) -> None:
        if state in DOCUMENT_ERROR_STATES:
            self.error = ErrorEntity(
                description=f"{error_type.value if error_type else error_type}: {error_message}",
                in_state=self.state,
            )
        else:
            self.error = None

        if state in END_STATES:
            self.add_event(
                DocumentProcessed(
                    document_id=self.pk,
                    document_type_code=self.document_type,
                    processing_result=DocumentProcessingResult.from_state(state),
                    error_message=error_message,
                ),
            )
        self.state = state

    def asdict(self):
        return {
            "pk": self.pk,
            "title": self.title,
            "state": self.state,
            "files": [asdict(file) for file in self.files],
            "date": self.date,
            "document_type": self.document_type,
            "sub_type": self.sub_type,
            "source_code": self.source_code,
            "reviewer": self.reviewer,
            "labels": [asdict(label) for label in self.labels] if self.labels is not None else self.labels,
            "language": self.language,
            "engine": self.engine,
            "llm_type": self.llm_type,
            "parent_id": self.parent_id,
            "group": self.group and self.group.asdict(),
            "container_type": self.container_type,
            "container_metadata": asdict(self.container_metadata)
            if self.container_metadata is not None
            else self.container_metadata,
            "scraped_metadata": asdict(self.scraped_metadata) if self.scraped_metadata is not None else self.scraped_metadata,
            "communication": asdict(self.communication) if self.communication is not None else self.communication,
            "preview_documents": [asdict(preview_document) for preview_document in self.preview_documents]
            if self.preview_documents is not None
            else self.preview_documents,
            "processing_documents": [asdict(processing_document) for processing_document in self.processing_documents]
            if self.processing_documents is not None
            else self.processing_documents,
            "error": asdict(self.error) if self.error is not None else self.error,
            "assigned_relations": [asdict(relation) for relation in self.assigned_relations],
            "assignment_status": self.assignment_status,
            "priority": self.priority,
            "parsing_features": sorted(self.parsing_features) if self.parsing_features else None,
            "needs_unification": self.needs_unification,
            "needs_extraction": self.needs_extraction,
            "needs_parsing": self.needs_parsing,
            "needs_validation": self.needs_validation,
            "needs_review": self.needs_review,
            "needs_output_exporting": self.needs_output_exporting,
        }

    def update(self, document_entity: "DocumentEntity"):
        self.title = document_entity.title
        self.files = document_entity.files
        self.date = document_entity.date
        self.document_type = document_entity.document_type
        self.sub_type = document_entity.sub_type
        self.source_code = document_entity.source_code
        self.reviewer = document_entity.reviewer
        self.language = document_entity.language
        self.engine = document_entity.engine
        self.llm_type = document_entity.llm_type
        self.container_metadata = document_entity.container_metadata
        self.scraped_metadata = document_entity.scraped_metadata
        self.preview_documents = document_entity.preview_documents
        self.processing_documents = document_entity.processing_documents
        self.parent_id = document_entity.parent_id
        self.assigned_relations = self.assigned_relations
        self.update_state(document_entity.state)

    def partially_update(self, document_fields: Dict[str, Any]):
        for document_field, value in document_fields.items():
            setattr(self, document_field, value)

    def enrich_events(self) -> None:
        for event in self.events:
            event.id = self.pk

    def _check_validation_availability(self):
        allowed_states = {
            DocumentStateEnum.DATA_EXTRACTION,
            DocumentStateEnum.COMPLETED,
            DocumentStateEnum.FAILED,
            DocumentStateEnum.IN_REVIEW,
        }
        if self.state not in allowed_states:
            raise DocumentValidationError(
                f"Can't validate document ({self.pk}) in state {self.state}",
            )


@dataclass(frozen=True)
class DocumentLogEntity:
    action: DocumentLogEnum
    previous: str
    current: str
    document_id: str
    pk: Optional[str] = None
    created_at: Optional[datetime] = None
    actor: Optional[ActorEnum] = None


@dataclass
class DocumentMetadata:
    document_id: DocumentEntityPk
    metadata: dict[str, Any] = field(default_factory=dict)
