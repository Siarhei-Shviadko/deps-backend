# flake8: noqa WPS221, WPS232
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deps_documents.domain.constants import (
    ContainerTypesEnum,
    DocumentAssignmentStatusEnum,
    DocumentPriorityEnum,
    DocumentStateEnum,
)
from deps_documents.domain.entities import (
    BlobFile,
    CommunicationEntity,
    ContainerEmailMetadata,
    DocumentEntity,
    DocumentEntityPk,
    ErrorEntity,
    LabelEntity,
    RelationEntity,
    Reviewer,
)

from .blob_file import BlobFileModel
from .comment import CommentsListModel
from .container import ContainerEmailMetadataModel
from .error import ErrorModel
from .group_info import SerializedGroupInfo
from .label import LabelModel
from .relation import RelationModel
from .reviewer import ReviewerModel


class DocumentModel(BaseModel):
    pk: Optional[str] = Field(None, alias="_id")
    parent_id: Optional[str] = Field(None, alias="parentId")

    title: str
    state: DocumentStateEnum
    files: list[BlobFileModel]
    document_type: Optional[str] = Field(None, alias="documentType")
    sub_type: Optional[str] = Field(None, alias="modelName")
    date: Optional[str] = None
    source_code: Optional[str] = Field(None, alias="source")
    reviewer: Optional[ReviewerModel] = None
    labels: list[LabelModel] = Field(default_factory=list)
    language: Optional[str] = None
    engine: Optional[str] = None
    group_id: Optional[str] = Field(None, alias="groupId", deprecated=True)
    group_info: Optional[SerializedGroupInfo] = Field(None, alias="groupInfo")
    llm_type: Optional[str] = Field(None, alias="llmType")
    communication: Optional[CommentsListModel] = None
    preview_documents: Optional[dict[str, BlobFileModel]] = Field(None, alias="previewDocuments")
    processing_documents: Optional[dict[str, BlobFileModel]] = Field(None, alias="processingDocuments")
    error: Optional[ErrorModel] = None
    container_type: Optional[ContainerTypesEnum] = Field(None, alias="containerType")
    container_metadata: Optional[ContainerEmailMetadataModel] = Field(None, alias="containerMetadata")
    assigned_relations: list[RelationModel] = Field(default_factory=list, alias="assignedRelations")
    assignment_status: Optional[DocumentAssignmentStatusEnum] = Field(
        DocumentAssignmentStatusEnum.UNASSIGNED,
        alias="assignmentStatus",
    )
    priority: Optional[DocumentPriorityEnum] = DocumentPriorityEnum.LOW

    model_config = ConfigDict(use_enum_values=True, populate_by_name=True, from_attributes=True)

    @classmethod
    def from_domain(cls, doc_entity: DocumentEntity) -> "DocumentModel":
        return cls(
            pk=doc_entity.pk,
            parent_id=doc_entity.parent_id,
            title=doc_entity.title,
            state=doc_entity.state,
            files=[BlobFileModel.model_validate(blob_file) for blob_file in doc_entity.files],
            document_type=doc_entity.document_type,
            sub_type=doc_entity.sub_type,
            date=doc_entity.date.isoformat() if doc_entity.date else None,
            source_code=doc_entity.source_code,
            reviewer=ReviewerModel.model_validate(doc_entity.reviewer) if doc_entity.reviewer else None,
            labels=[LabelModel.model_validate(label) for label in doc_entity.labels],
            language=doc_entity.language,
            engine=doc_entity.engine,
            llm_type=doc_entity.llm_type,
            communication=CommentsListModel.model_validate(doc_entity.communication) if doc_entity.communication else None,
            preview_documents={str(num): value for num, value in enumerate(doc_entity.preview_documents, 1)}
            if doc_entity.preview_documents
            else {},
            processing_documents={str(num): value for num, value in enumerate(doc_entity.processing_documents, 1)}
            if doc_entity.processing_documents
            else {},
            error=ErrorModel.model_validate(doc_entity.error) if doc_entity.error else None,
            container_type=doc_entity.container_type,
            container_metadata=ContainerEmailMetadataModel.model_validate(doc_entity.container_metadata)
            if doc_entity.container_metadata
            else None,
            assigned_relations=[
                RelationModel.model_validate(relation_entity) for relation_entity in doc_entity.assigned_relations
            ],
            assignment_status=doc_entity.assignment_status,
            priority=doc_entity.priority,
            group_id=doc_entity.group_id,
            group_info=doc_entity.group and SerializedGroupInfo.from_domain(doc_entity.group),
        )

    def to_domain(self):
        return DocumentEntity(
            pk=DocumentEntityPk(self.pk),
            parent_id=DocumentEntityPk(self.parent_id) if self.parent_id is not None else None,
            title=self.title,
            state=self.state,
            files=[BlobFile(blob_name=blob_file.blob_name) for blob_file in self.files] if self.files else [],
            document_type=self.document_type,
            sub_type=self.sub_type,
            date=datetime.fromisoformat(self.date) if self.date else None,
            source_code=self.source_code,
            reviewer=Reviewer(
                id=self.reviewer.id,
                email=self.reviewer.email,
                first_name=self.reviewer.first_name,
                last_name=self.reviewer.last_name,
            )
            if self.reviewer
            else None,
            labels=[LabelEntity(pk=label.pk, name=label.name) for label in self.labels] if self.labels else [],  # type: ignore
            language=self.language,
            engine=self.engine,
            communication=CommunicationEntity(**self.communication.model_dump(by_alias=False)) if self.communication else None,
            preview_documents=[
                BlobFile(blob_name=value.blob_name)
                for _, value in sorted(self.preview_documents.items(), key=lambda doc: int(doc[0]))
            ]
            if self.preview_documents
            else [],
            processing_documents=[
                BlobFile(blob_name=value.blob_name)
                for _, value in sorted(self.processing_documents.items(), key=lambda doc: int(doc[0]))
            ]
            if self.processing_documents
            else [],
            error=ErrorEntity(**self.error.model_dump(by_alias=False)) if self.error else None,
            container_type=self.container_type,
            container_metadata=ContainerEmailMetadata(**self.container_metadata.model_dump(by_alias=False))
            if self.container_metadata
            else None,
            assigned_relations=[RelationEntity(**relation.model_dump(by_alias=False)) for relation in self.assigned_relations]
            if self.assigned_relations
            else [],
            assignment_status=self.assignment_status,
            priority=self.priority,
            group=self.group_info and self.group_info.to_domain(),
        )

    @field_validator("pk", mode="before")
    def cast_pk_to_str(cls, v):  # noqa: N805
        return str(v) if v is not None else v


class PartialDocumentModel(DocumentModel):
    pk: Optional[str] = Field(None, alias="_id")
    title: Optional[str] = None
    state: Optional[DocumentStateEnum] = None
    files: Optional[list[BlobFileModel]] = Field(default_factory=list)
    labels: Optional[list[LabelModel]] = Field(default_factory=list)

    assigned_relations: Optional[list[RelationModel]] = Field(default_factory=list, alias="assignedRelations")
    assignment_status: Optional[DocumentAssignmentStatusEnum] = Field(None, alias="assignmentStatus")
    priority: Optional[DocumentPriorityEnum] = None
