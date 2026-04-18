from typing import Any, Optional

from deps_documents.domain.constants import DocumentStateEnum, ErrorType
from deps_documents.domain.entities import Reviewer
from deps_documents.infrastructure.access_management.document_access_manager import (
    IDocumentServiceAccessManager,
)

from .service import DocumentService

__all__ = ["DocumentAccessService"]


class DocumentAccessService:
    def __init__(
        self,
        document_service: DocumentService,
        document_access_manager: IDocumentServiceAccessManager,
    ):
        self._document_service = document_service
        self._document_access_manager = document_access_manager

    def create_document(
        self,
        document_name: str,
        document_type: str,
        language: str,
        engine: str,
        blob_name: str,
        tenant: str,
        llm_type: Optional[str],
        reviewer: Optional[Reviewer] = None,
        metadata: dict[str, Any] = None,
        parent_id: Optional[str] = None,
    ) -> str:
        self._document_access_manager.check_is_accessible_create()
        document_pk = self._document_service.create_document(
            document_name=document_name,
            document_type=document_type,
            language=language,
            engine=engine,
            llm_type=llm_type,
            blob_name=blob_name,
            tenant=tenant,
            reviewer=reviewer,
            metadata=metadata,
            parent_id=parent_id,
        )
        self._document_access_manager.add_permissions_after_creating(document_pk)  # type: ignore

        return document_pk

    def update_state(
        self,
        document_id: str,
        state: DocumentStateEnum,
        error_type: Optional[ErrorType] = None,
        error_message: Optional[str] = None,
    ) -> None:
        self._document_access_manager.check_is_accessible_write([document_id])  # type: ignore
        self._document_service.update_state(document_id, state, error_type, error_message)

    def unassign_reviewer(self, document_id: str) -> None:
        self._document_access_manager.check_is_accessible_write([document_id])  # type: ignore
        self._document_service.unassign_reviewer(document_id)

    def save_metadata(self, document_id: str, metadata: dict[str, Any]) -> None:
        self._document_access_manager.check_is_accessible_write([document_id])  # type: ignore
        self._document_service.save_metadata(document_id, metadata)
