import logging
from typing import Any, Callable, Optional

from deps_documents.application.document_type import DocumentTypeService
from deps_documents.domain.constants import DocumentStateEnum, ErrorType
from deps_documents.domain.entities import DocumentEntityPk, DocumentMetadata, Reviewer
from deps_documents.domain.entities.factory import DocumentCreatorFactory
from deps_documents.domain.events.events import DocumentStateUpdated
from deps_documents.domain.exceptions import DocumentMetadataNotFoundError
from deps_documents.domain.interfaces import IDocumentUnitOfWork

__all__ = ["DocumentService"]


class DocumentService:
    def __init__(
        self,
        uow: Callable[..., IDocumentUnitOfWork],
        document_type_service: DocumentTypeService,
    ):
        self._uow = uow
        self._document_type_service = document_type_service
        self._logger = logging.getLogger(self.__class__.__name__)

    def create_document(
        self,
        document_name: str,
        document_type: str,
        language: str,
        engine: str,
        llm_type: Optional[str],
        blob_name: str,
        tenant: str,
        reviewer: Optional[Reviewer] = None,
        metadata: dict[str, Any] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        if document_type:
            self._document_type_service.find_by_id_for_tenant(document_type_id=document_type, tenant_id=tenant)

        document_creator = DocumentCreatorFactory.get_creator(blob_name)

        document_entity = document_creator.generate_new_document(
            title=document_name,
            blob_name=blob_name,
            language=language,
            engine=engine,
            llm_type=llm_type,
            document_type=document_type,
            source=None,
            reviewer=reviewer,
            parent_id=parent_id,
        )
        with self._uow() as uow:
            document_entity = uow.document.add(document_entity)

            if metadata:
                document_metadata = DocumentMetadata(
                    document_id=document_entity.pk,
                    metadata=metadata,
                )
                uow.document.upsert_document_metadata(document_metadata)

            uow.commit()

        return document_entity.pk

    def update_state(
        self,
        document_id: str,
        state: DocumentStateEnum,
        error_type: Optional[ErrorType] = None,
        error_message: Optional[str] = None,
    ) -> None:
        self._logger.info("Updating document `%s` state to `%s`", document_id, state)

        with self._uow() as uow:
            document_entity = uow.document.get(DocumentEntityPk(document_id))
            document_entity.update_state(state=state, error_type=error_type, error_message=error_message)
            uow.add_events(
                [
                    DocumentStateUpdated(
                        document_id=document_id,
                        state=state.value,
                        metadata=self._get_document_metadata(DocumentEntityPk(document_id)).metadata,
                        error_in_state=document_entity.error.in_state if document_entity.error else None,
                    ),
                    *document_entity.pop_all_events(),
                ],
            )
            uow.document.update(document_entity)
            uow.commit()

    def unassign_reviewer(self, document_id: str) -> None:
        with self._uow() as uow:
            document_entity = uow.document.get(DocumentEntityPk(document_id))
            document_entity.unassign_reviewer()
            uow.document.update(document_entity)
            uow.commit()

    def save_metadata(self, document_id: str, metadata: dict[str, Any]) -> None:
        with self._uow() as uow:
            document_metadata = DocumentMetadata(document_id=document_id, metadata=metadata)  # type: ignore
            uow.document.upsert_document_metadata(document_metadata)
            uow.commit()

    def _get_document_metadata(self, document_entity_pk: DocumentEntityPk) -> DocumentMetadata:
        with self._uow() as uow:
            try:
                metadata = uow.document.get_document_metadata(document_entity_pk)
                uow.commit()
            except DocumentMetadataNotFoundError:
                return DocumentMetadata(document_id=document_entity_pk)

        return metadata
