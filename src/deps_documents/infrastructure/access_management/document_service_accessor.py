from typing import Any, Dict, List, Optional

from deps_documents.domain.constants import PipelineStepsEnum
from deps_documents.domain.dtos import (
    DocumentFilesDataObject,
    DocumentListDataObject,
    DocumentListFilterObject,
)
from deps_documents.domain.entities import (
    CommentEntity,
    DocumentEntity,
    DocumentEntityPk,
    DocumentMetadata,
    LabelEntityPk,
    Reviewer,
)
from deps_documents.domain.exceptions import (
    DocumentForbiddenError,
    DocumentNotFoundError,
)
from deps_documents.domain.interfaces import IDocumentService
from deps_documents.domain.services import DocumentService
from deps_documents.infrastructure.access_management.document_access_manager import (
    IDocumentServiceAccessManager,
)
from deps_documents.infrastructure.access_management.label_access_manager import (
    ILabelServiceAccessManager,
)


class DocumentServiceAccessor(IDocumentService):  # pylint: disable=too-many-public-methods
    def __init__(
        self,
        document_service: DocumentService,
        document_access_manager: IDocumentServiceAccessManager,
        label_access_manager: ILabelServiceAccessManager,
    ):
        self._document_service = document_service
        self._document_access_manager = document_access_manager
        self._label_access_manager = label_access_manager

    def add_comment(self, comment_entity: CommentEntity, document_entity_pk: DocumentEntityPk) -> CommentEntity:
        self._document_access_manager.check_is_accessible_write([document_entity_pk])

        return self._document_service.add_comment(comment_entity=comment_entity, document_entity_pk=document_entity_pk)

    def add_file(self, document_entity_pk: DocumentEntityPk, file_content: bytes, file_name: str) -> DocumentEntityPk:
        self._document_access_manager.check_is_accessible_write([document_entity_pk])

        return self._document_service.add_file(
            document_entity_pk=document_entity_pk,
            file_content=file_content,
            file_name=file_name,
        )

    def add_label(self, label_pk: LabelEntityPk, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        self._label_access_manager.check_is_accessible_read([label_pk])
        self._document_access_manager.check_is_accessible_write(document_entity_pks)

        return self._document_service.add_label(label_pk=label_pk, document_entity_pks=document_entity_pks)

    def assign_type(
        self,
        document_entity_pks: List[DocumentEntityPk],
        type_code: Optional[str],
        initial_assign: bool = False,
    ) -> List[DocumentEntity]:
        self._document_access_manager.check_is_accessible_write(document_entity_pks)

        return self._document_service.assign_type(
            document_entity_pks=document_entity_pks,
            type_code=type_code,
            initial_assign=initial_assign,
        )

    def batch_delete(self, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntityPk]:
        try:
            self._document_access_manager.check_is_accessible_write(document_entity_pks)
        except DocumentForbiddenError:
            raise DocumentNotFoundError(f"Documents with the following key(s) `{document_entity_pks}` not existing.")

        return self._document_service.batch_delete(document_entity_pks=document_entity_pks)

    def complete_review(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        self._document_access_manager.check_is_accessible_write([document_entity_pk])

        return self._document_service.complete_review(document_entity_pk=document_entity_pk)

    def create(self, document_entity: DocumentEntity) -> DocumentEntityPk:
        self._document_access_manager.check_is_accessible_create()
        document_entity_pk = self._document_service.create(document_entity=document_entity)
        self._document_access_manager.add_permissions_after_creating(document_entity_pk)

        return document_entity_pk

    def delete(self, document_entity_pk: DocumentEntityPk) -> bool:
        self._document_access_manager.check_is_accessible_write([document_entity_pk])

        return self._document_service.delete(document_entity_pk=document_entity_pk)

    def document_file(
        self,
        file_content: bytes,
        file_name: str,
        document_name: str,
        source: str,
        run_pipeline: bool,
        language: str,
        engine: str,
        llm_type: Optional[str],
        tenant: Optional[str],
        extraction_params: Optional[Dict[str, Any]] = None,
        document_type: Optional[str] = None,
        sub_type: Optional[str] = None,
        extract_data: bool = False,
        reviewer: Optional[Reviewer] = None,
        metadata: dict[str, Any] = None,
    ) -> DocumentEntityPk:
        self._document_access_manager.check_is_accessible_create()
        document_pk = self._document_service.document_file(
            file_content=file_content,
            file_name=file_name,
            document_name=document_name,
            source=source,
            run_pipeline=run_pipeline,
            language=language,
            engine=engine,
            llm_type=llm_type,
            tenant=tenant,
            document_type=document_type,
            sub_type=sub_type,
            extract_data=extract_data,
            extraction_params=extraction_params,
            reviewer=reviewer,
            metadata=metadata,
        )
        self._document_access_manager.add_permissions_after_creating(document_pk)

        return document_pk

    def extract_data(
        self,
        document_entity_pks: List[DocumentEntityPk],
        engine: Optional[str] = None,
    ) -> List[DocumentEntity]:
        self._document_access_manager.check_is_accessible_write(document_entity_pks)

        return self._document_service.extract_data(document_entity_pks=document_entity_pks, engine=engine)

    def get(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        res = self._document_service.get(document_entity_pk=document_entity_pk)
        self._document_access_manager.check_is_accessible_read([document_entity_pk])
        return res

    def get_descendants(self, document_entity_pk: DocumentEntityPk, include_containers: bool = False) -> List[DocumentEntity]:
        self._document_access_manager.check_is_accessible_read([document_entity_pk])

        return self._document_service.get_descendants(document_entity_pk)

    def get_document_files(self, document_entity_pk: DocumentEntityPk) -> DocumentFilesDataObject:
        self._document_access_manager.check_is_accessible_read([document_entity_pk])

        return self._document_service.get_document_files(document_entity_pk=document_entity_pk)

    def get_document_list(self, options: DocumentListFilterObject) -> DocumentListDataObject:
        self._document_access_manager.patch_filter(options)
        return self._document_service.get_document_list(options=options)

    def get_brief_documents_info(self, document_pks: list[DocumentEntityPk]) -> list[dict]:
        self._document_access_manager.check_is_accessible_read(document_pks)

        return self._document_service.get_brief_documents_info(document_pks)

    def get_processed_images(self, document_entity_pk: DocumentEntityPk) -> DocumentFilesDataObject:
        self._document_access_manager.check_is_accessible_read([document_entity_pk])

        return self._document_service.get_processed_images(document_entity_pk=document_entity_pk)

    def identify(self, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        self._document_access_manager.check_is_accessible_write(document_entity_pks)

        return self._document_service.identify(document_entity_pks=document_entity_pks)

    def remove_label(self, label_pk: LabelEntityPk, document_entity_pk: DocumentEntityPk) -> bool:
        self._document_access_manager.check_is_accessible_write([document_entity_pk])

        return self._document_service.remove_label(label_pk=label_pk, document_entity_pk=document_entity_pk)

    def get_document_metadata(self, document_entity_pk: DocumentEntityPk) -> DocumentMetadata:
        self._document_access_manager.check_is_accessible_read([document_entity_pk])

        return self._document_service.get_document_metadata(document_entity_pk)

    def upsert_document_metadata(self, document_metadata: DocumentMetadata) -> DocumentMetadata:
        self._document_access_manager.check_is_accessible_write([document_metadata.document_id])

        return self._document_service.upsert_document_metadata(document_metadata)

    def delete_document_metadata(self, document_metadata: DocumentMetadata) -> None:
        self._document_access_manager.check_is_accessible_write([document_metadata.document_id])

        self._document_service.delete_document_metadata(document_metadata)

    def reset_reviewer(self, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        self._document_access_manager.check_is_accessible_write(document_entity_pks)

        return self._document_service.reset_reviewer(document_entity_pks=document_entity_pks)

    def retry_last_step(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        self._document_access_manager.check_is_accessible_write([document_entity_pk])

        return self._document_service.retry_last_step(document_entity_pk=document_entity_pk)

    def run_pipeline(
        self,
        document_entity_pks: List[DocumentEntityPk],
        engine: str,
        language: Optional[str] = None,
        need_extraction: bool = True,
        need_identification: bool = True,
    ) -> List[DocumentEntity]:
        self._document_access_manager.check_is_accessible_write(document_entity_pks)

        return self._document_service.run_pipeline(
            document_entity_pks=document_entity_pks,
            engine=engine,
            language=language,
            need_extraction=need_extraction,
            need_identification=need_identification,
        )

    def run_pipeline_from_step(
        self,
        document_entity_pks: List[DocumentEntityPk],
        step: PipelineStepsEnum,
        language: str,
        engine: Optional[str] = None,
    ) -> List[DocumentEntity]:
        self._document_access_manager.check_is_accessible_write(document_entity_pks)

        return self._document_service.run_pipeline_from_step(
            document_entity_pks=document_entity_pks,
            step=step,
            language=language,
            engine=engine,
        )

    def start_review(
        self,
        document_entity_pks: List[DocumentEntityPk],
        reviewer: Optional[Reviewer] = None,
        reassign_reviewer: bool = False,
    ) -> List[DocumentEntity]:
        self._document_access_manager.check_is_accessible_write(document_entity_pks)

        return self._document_service.start_review(
            document_entity_pks=document_entity_pks,
            reviewer=reviewer,
            reassign_reviewer=reassign_reviewer,
        )

    def update(self, document_entity: DocumentEntity) -> DocumentEntityPk:
        self._document_access_manager.check_is_accessible_write([document_entity.pk])

        return self._document_service.update(document_entity=document_entity)

    def partially_update(
        self,
        document_entity_pk: DocumentEntityPk,
        document_fields: Dict[str, Any],
    ) -> DocumentEntityPk:
        self._document_access_manager.check_is_accessible_write([document_entity_pk])

        return self._document_service.partially_update(
            document_entity_pk=document_entity_pk,
            document_fields=document_fields,
        )

    def update_priorities(self) -> None:
        raise NotImplementedError("User cannot update priorities")

    def validate(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        self._document_access_manager.check_is_accessible_write([document_entity_pk])
        return self._document_service.validate(document_entity_pk)
