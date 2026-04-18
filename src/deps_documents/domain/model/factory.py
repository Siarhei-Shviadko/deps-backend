import os
from datetime import datetime, timezone
from typing import Optional

from deps_documents.domain.constants import ContainerTypesEnum, DocumentStateEnum
from deps_documents.domain.entities import (
    BlobFile,
    CommunicationEntity,
    DocumentEntity,
    DocumentEntityPk,
    GroupEntity,
    ParsingFeature,
    Reviewer,
    ScrapedMetadataEntity,
)
from deps_documents.domain.entities.document import ContainerEmailMetadata

from .reviewer_info import ReviewerInfo

__all__ = ["DocumentCreatorFactory"]


class PlainDocumentCreator:
    @classmethod
    def generate_new_document(
        cls,
        title: str,
        blob_name: str,
        document_type_id: Optional[str] = None,
        group: Optional[GroupEntity] = None,
        parent_id: Optional[DocumentEntityPk] = None,
        language: Optional[str] = None,
        engine: Optional[str] = None,
        llm_type: Optional[str] = None,
        state=DocumentStateEnum.NEW,
        reviewer_info: Optional[ReviewerInfo] = None,
        assign_to_me: bool = False,
        parsing_features: Optional[set[ParsingFeature]] = None,
        needs_unification: bool = False,
        needs_extraction: bool = False,
        needs_parsing: Optional[bool] = None,
        needs_validation: Optional[bool] = None,
        needs_review: Optional[str] = None,
        needs_output_exporting: Optional[bool] = None,
    ):
        if assign_to_me and reviewer_info is not None:
            reviewer = cls._make_reviewer(reviewer_info)
        else:
            reviewer = None

        return DocumentEntity(
            pk=None,
            parent_id=parent_id,
            group=group,
            scraped_metadata=ScrapedMetadataEntity(),
            communication=CommunicationEntity(),
            title=title,
            state=state,
            files=[BlobFile(blob_name=blob_name)],
            document_type=document_type_id,
            date=datetime.now(tz=timezone.utc),
            reviewer=reviewer,
            language=language,
            engine=engine,
            llm_type=llm_type,
            parsing_features=parsing_features,
            needs_unification=needs_unification,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
            needs_validation=needs_validation,
            needs_review=needs_review,
            needs_output_exporting=needs_output_exporting,
        )

    @staticmethod
    def _make_reviewer(reviewer_data: ReviewerInfo) -> Reviewer:
        return Reviewer(
            id=reviewer_data.get("subject"),
            email=reviewer_data.get("email"),
            first_name=reviewer_data.get("first_name"),
            last_name=reviewer_data.get("last_name"),
        )


class EmailDocumentCreator:
    @classmethod
    def generate_new_document(
        cls,
        title: str,
        blob_name: str,
        document_type_id: Optional[str] = None,
        group: Optional[GroupEntity] = None,
        parent_id: Optional[DocumentEntityPk] = None,
        language: Optional[str] = None,
        engine: Optional[str] = None,
        llm_type: Optional[str] = None,
        state=DocumentStateEnum.NEW,
        reviewer_info: Optional[ReviewerInfo] = None,
        assign_to_me: bool = False,
        parsing_features: Optional[set[ParsingFeature]] = None,
        needs_unification: bool = False,
        needs_extraction: bool = False,
        needs_parsing: Optional[bool] = None,
        needs_validation: Optional[bool] = None,
        needs_review: Optional[str] = None,
        needs_output_exporting: Optional[bool] = None,
        **container_metadata,
    ):
        document_entity = PlainDocumentCreator.generate_new_document(
            title=title,
            blob_name=blob_name,
            document_type_id=document_type_id,
            group=group,
            parent_id=parent_id,
            language=language,
            engine=engine,
            llm_type=llm_type,
            state=state,
            reviewer_info=reviewer_info,
            assign_to_me=assign_to_me,
            parsing_features=parsing_features,
            needs_unification=needs_unification,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
            needs_validation=needs_validation,
            needs_output_exporting=needs_output_exporting,
            needs_review=needs_review,
        )
        document_entity.container_type = ContainerTypesEnum.EMAIL
        document_entity.container_metadata = ContainerEmailMetadata(**container_metadata)

        return document_entity


class DocumentCreatorFactory:
    creators_map = {
        # Emails
        "eml": EmailDocumentCreator,
        "msg": EmailDocumentCreator,
    }
    default_creator = PlainDocumentCreator

    @classmethod
    def get_creator(cls, file_name: str):
        return cls.creators_map.get(cls._get_file_extension(file_name), cls.default_creator)

    @staticmethod
    def _get_file_extension(file_name: str) -> str:
        _, extension = os.path.splitext(file_name)

        return extension.lstrip(".").lower()
