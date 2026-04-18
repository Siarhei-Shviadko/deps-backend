import os
from datetime import datetime, timezone

from deps_documents.domain.constants import ContainerTypesEnum, DocumentStateEnum
from deps_documents.domain.entities import (
    BlobFile,
    CommunicationEntity,
    DocumentEntity,
    ScrapedMetadataEntity,
)
from deps_documents.domain.entities.document import ContainerEmailMetadata


class PlainDocumentCreator:
    @staticmethod
    def generate_new_document(
        source,
        title,
        blob_name,
        language,
        engine,
        document_type,
        llm_type=None,
        sub_type=None,
        parent_id=None,
        reviewer=None,
        state=DocumentStateEnum.NEW,
        **container_metadata,
    ):
        return DocumentEntity(
            pk=None,
            parent_id=parent_id,
            scraped_metadata=ScrapedMetadataEntity(),
            communication=CommunicationEntity(),
            title=title,
            state=state,
            files=[BlobFile(blob_name=blob_name)],
            document_type=document_type,
            sub_type=sub_type,
            date=datetime.now(tz=timezone.utc),
            source_code=source,
            reviewer=reviewer,
            language=language,
            engine=engine,
            llm_type=llm_type,
        )


class EmailDocumentCreator:
    @staticmethod
    def generate_new_document(
        source,
        title,
        blob_name,
        language,
        engine,
        document_type,
        llm_type=None,
        sub_type=None,
        parent_id=None,
        reviewer=None,
        state=DocumentStateEnum.NEW,
        **container_metadata,
    ):
        document_entity = PlainDocumentCreator.generate_new_document(
            source=source,
            title=title,
            blob_name=blob_name,
            reviewer=reviewer,
            language=language,
            engine=engine,
            llm_type=llm_type,
            document_type=document_type,
            parent_id=parent_id,
            sub_type=sub_type,
            state=state,
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
    def _get_file_extension(filename) -> str:
        _, extension = os.path.splitext(filename)
        return extension.lstrip(".").lower()
