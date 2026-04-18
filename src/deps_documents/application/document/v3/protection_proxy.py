from typing import Any, Optional

from deps_documents.domain.entities import (
    DocumentEntityPk,
    LabelEntityPk,
    ParsingFeature,
)
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

    def create_document_with_existing_file(
        self,
        document_name: str,
        tenant_id: str,
        document_type_id: Optional[str],
        group_id: Optional[str],
        blob_name: str,
        engine: Optional[str],
        language: Optional[str],
        llm_type: Optional[str],
        assign_to_me: bool,
        parsing_features: Optional[set[ParsingFeature]] = None,
        metadata: Optional[dict[str, Any]] = None,
        parent_id: Optional[str] = None,
        needs_unification: bool = False,
        needs_extraction: bool = False,
        needs_parsing: bool = False,
        start_processing: bool = True,
        label_ids: Optional[list[LabelEntityPk]] = None,
    ) -> str:
        self._document_access_manager.check_is_accessible_create()
        if label_ids:
            self._document_access_manager.check_can_add_labels(label_ids)

        document = self._document_service.create_document_with_existing_file(
            document_name=document_name,
            document_type_id=document_type_id,
            group_id=group_id,
            tenant_id=tenant_id,
            blob_name=blob_name,
            engine=engine,
            language=language,
            llm_type=llm_type,
            assign_to_me=assign_to_me,
            parsing_features=parsing_features,
            metadata=metadata,
            needs_unification=needs_unification,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
            parent_id=parent_id,
            label_ids=label_ids,
        )

        self._document_access_manager.add_permissions_after_creating(document.pk)  # type: ignore

        if start_processing:
            self._document_service.initiate_document_processing(
                document=document,
                tenant_id=tenant_id,
                document_type_id=document_type_id,
                group_id=group_id,
                engine=engine,
                language=language,
                llm_type=llm_type,
                parsing_features=parsing_features,
                needs_unification=needs_unification,
                needs_extraction=needs_extraction,
                needs_parsing=needs_parsing,
            )

        return document.pk

    def create_document(
        self,
        document_name: str,
        tenant_id: str,
        document_type_id: Optional[str],
        group_id: Optional[str],
        file_name: str,
        file_content: bytes,
        engine: Optional[str],
        language: Optional[str],
        llm_type: Optional[str],
        assign_to_me: bool,
        parsing_features: Optional[set[ParsingFeature]] = None,
        metadata: dict[str, Any] = None,
        parent_id: Optional[str] = None,
        needs_unification: bool = False,
        needs_extraction: bool = False,
        needs_parsing: Optional[bool] = None,
        needs_validation: Optional[bool] = None,
        needs_review: Optional[str] = None,
        needs_output_exporting: Optional[bool] = None,
        label_ids: Optional[list[LabelEntityPk]] = None,
    ) -> str:
        self._document_access_manager.check_is_accessible_create()
        if label_ids:
            self._document_access_manager.check_can_add_labels(label_ids)

        document = self._document_service.create_document(
            document_name=document_name,
            document_type_id=document_type_id,
            group_id=group_id,
            tenant_id=tenant_id,
            file_name=file_name,
            file_content=file_content,
            engine=engine,
            language=language,
            llm_type=llm_type,
            assign_to_me=assign_to_me,
            parsing_features=parsing_features,
            metadata=metadata,
            needs_unification=needs_unification,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
            needs_validation=needs_validation,
            needs_review=needs_review,
            needs_output_exporting=needs_output_exporting,
            parent_id=parent_id,
            label_ids=label_ids,
        )

        self._document_access_manager.add_permissions_after_creating(document.pk)  # type: ignore

        self._document_service.initiate_document_processing(
            document=document,
            tenant_id=tenant_id,
            document_type_id=document_type_id,
            group_id=group_id,
            engine=engine,
            language=language,
            llm_type=llm_type,
            parsing_features=parsing_features,
            needs_unification=needs_unification,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
            needs_validation=needs_validation,
            needs_review=needs_review,
            needs_output_exporting=needs_output_exporting,
        )

        return document.pk

    def create_document_from_file(
        self,
        document_name: str,
        tenant_id: str,
        document_type_id: str,
        group_id: Optional[str],
        file_name: str,
        file_content: bytes,
        engine: Optional[str],
        language: Optional[str],
        llm_type: Optional[str],
        assign_to_me: bool,
        parsing_features: Optional[set[ParsingFeature]] = None,
        metadata: Optional[dict[str, Any]] = None,
        parent_id: Optional[str] = None,
        needs_unification: bool = False,
        needs_extraction: bool = False,
        needs_parsing: bool = False,
    ) -> tuple[DocumentEntityPk, str]:
        self._document_access_manager.check_is_accessible_create()

        document = self._document_service.create_document(
            document_name=document_name,
            document_type_id=document_type_id,
            group_id=group_id,
            tenant_id=tenant_id,
            file_name=file_name,
            file_content=file_content,
            engine=engine,
            language=language,
            llm_type=llm_type,
            assign_to_me=assign_to_me,
            parsing_features=parsing_features,
            metadata=metadata,
            needs_unification=needs_unification,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
            parent_id=parent_id,
        )

        self._document_access_manager.add_permissions_after_creating(document.pk)  # type: ignore

        self._document_service.initiate_document_processing(
            document=document,
            tenant_id=tenant_id,
            document_type_id=document_type_id,
            group_id=group_id,
            engine=engine,
            language=language,
            llm_type=llm_type,
            parsing_features=parsing_features,
            needs_unification=needs_unification,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
        )

        return document.pk, document.title

    def assign_document_type(self, tenant_id: str, document_id: str, document_type_id: Optional[str]) -> None:
        self._document_access_manager.check_is_accessible_write(document_entity_pks=[DocumentEntityPk(document_id)])

        self._document_service.assign_document_type(
            tenant_id=tenant_id,
            document_id=document_id,
            document_type_id=document_type_id,
        )

    def start_batch_processing(self, document_ids: list[str], tenant_id: str) -> None:
        self._document_access_manager.check_is_accessible_read(
            document_entity_pks=[DocumentEntityPk(document_id) for document_id in document_ids],
        )

        self._document_service.start_batch_processing(document_ids=document_ids, tenant_id=tenant_id)
