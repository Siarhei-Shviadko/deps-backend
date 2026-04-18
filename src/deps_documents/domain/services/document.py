# flake8: noqa WPS203
import os
from collections import namedtuple
from contextlib import suppress
from typing import Any, Callable, Dict, List, Optional

from deps_object_storage import FileNotFound, ObjectStorage

from deps_documents.application import DocumentTypeService
from deps_documents.domain.constants import (
    START_REVIEW_STATES,
    UNACCEPTABLE_IDENTIFICATION_DOCUMENT_STATES,
    DocumentStateEnum,
    PipelineStepsEnum,
)
from deps_documents.domain.dtos import (
    DocumentFilesDataObject,
    DocumentListDataObject,
    DocumentListFilterObject,
    ListResponseMetaDataObject,
    PerPageOptions,
)
from deps_documents.domain.entities import (
    BlobFile,
    CommentEntity,
    DocumentEntity,
    DocumentEntityPk,
    DocumentMetadata,
    LabelEntityPk,
    Reviewer,
)
from deps_documents.domain.entities.factory import DocumentCreatorFactory
from deps_documents.domain.events import (
    DeleteFiles,
    DocumentAssigned,
    DocumentDeleted,
    DocumentFieldsUpdated,
    DocumentStateUpdated,
    DocumentTypeChanged,
    DocumentUpdated,
)
from deps_documents.domain.exceptions import (
    DocumentAlreadyHasDocumentType,
    DocumentExtractDataError,
    DocumentImagesAccessError,
    DocumentLastStepRetrievingError,
    DocumentMetadataNotFoundError,
    DocumentNotAcceptableStateError,
    DocumentReviewerError,
    DocumentReviewStateError,
    DocumentStateError,
)
from deps_documents.domain.interfaces import (
    IDocumentService,
    IDocumentUnitOfWork,
    IPipelineManagerService,
    IPriorityManager,
)
from deps_documents.domain.interfaces.services import IValidationService
from deps_documents.domain.specifications import (
    CanBeRetried,
    CanBeRetriedExtraction,
    CanBeRetriedIdentification,
    CanBeRetriedPreprocessing,
)
from deps_documents.domain.specifications.document_change_specification import (
    CanBeChangedSpecification,
)
from deps_documents.infrastructure.repositories.helpers import batch_pk_validate
from deps_documents.infrastructure.services import CorleoneService

ExtractionMetadata = namedtuple("ExtractionMetadata", "engine extraction_type")


class DocumentService(IDocumentService):  # noqa: WPS214
    REPLACE_FILE_CONTENT_IF_EXISTS = True

    def __init__(
        self,
        blob_service: ObjectStorage,
        pipeline_manager: IPipelineManagerService,
        priority_manager: IPriorityManager,
        validation_service: IValidationService,
        corleone_service: CorleoneService,
        document_type_service: DocumentTypeService,
        uow: Callable[..., IDocumentUnitOfWork],
    ):
        self._blob_service = blob_service
        self._validation_service = validation_service
        self._corleone_service = corleone_service
        self._document_type_service = document_type_service
        self._pipeline_manager = pipeline_manager
        self._priority_manager = priority_manager
        self._uow = uow

    def add_comment(self, comment_entity: CommentEntity, document_entity_pk: DocumentEntityPk) -> CommentEntity:
        with self._uow() as uow:
            comment = uow.comment.add(comment_entity=comment_entity, document_entity_pk=document_entity_pk)
            uow.commit()
        return comment

    def add_file(self, document_entity_pk: DocumentEntityPk, file_content: bytes, file_name: str) -> DocumentEntityPk:
        blob_name = self._blob_service.upload(
            path=file_name, content=file_content, replace_if_exists=self.REPLACE_FILE_CONTENT_IF_EXISTS
        )

        with self._uow() as uow:
            documents = uow.document.select_for_update([document_entity_pk])
            document_entity = documents[0]
            file = BlobFile(blob_name=blob_name)
            document_entity.files.append(file)
            document_entity = uow.document.update(document_entity)
            uow.commit()

        return document_entity.pk

    def add_label(self, label_pk: LabelEntityPk, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        with self._uow() as uow:
            document_entity_pks = uow.document.add_label(label_pk, document_entity_pks)
            pks = uow.document.find_by_pks(document_entity_pks)
            uow.commit()
        return pks

    def assign_type(
        self, document_entity_pks: List[DocumentEntityPk], type_code: str, initial_assign: bool = False
    ) -> List[DocumentEntity]:
        if initial_assign:
            updated_documents = self._set_up_document_type(document_entity_pks, type_code)
        else:
            updated_documents = self._change_document_type(document_entity_pks, type_code)
        return updated_documents

    def batch_delete(self, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntityPk]:  # noqa: WPS210
        valid_document_pks = sorted(batch_pk_validate(document_entity_pks), reverse=True)
        deleted_document_pks = []
        with self._uow() as uow:
            for document_pk in valid_document_pks:
                if self.delete(document_pk):
                    deleted_document_pks.append(DocumentEntityPk(str(document_pk)))
            uow.commit()
        return deleted_document_pks

    def complete_review(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        with self._uow() as uow:
            document_entities = uow.document.select_for_update([document_entity_pk])
            document_entity = document_entities[0]
            if self._corleone_service.is_extracted_data_exists(document_entity_pk):
                self._validation_service.send_document_to_validation(document_entity.pk)
                document_entity.state = DocumentStateEnum.VALIDATION
                updated_document_entity = uow.document.update(document_entity)
            else:
                document_entity.state = DocumentStateEnum.COMPLETED
                updated_document_entity = uow.document.update(document_entity)

            uow.commit()
        return updated_document_entity

    def create(self, document_entity: DocumentEntity) -> DocumentEntityPk:
        with self._uow() as uow:
            pk = uow.document.add(document_entity).pk
            uow.commit()
        return pk

    def delete(self, document_entity_pk: DocumentEntityPk) -> bool:
        with self._uow() as uow:
            document = uow.document.get(document_entity_pk)
            documents_to_delete = [document]
            if document.container_type is not None:
                documents_to_delete.extend(
                    uow.document.get_descendants(document.pk, include_containers=True),
                )

            for document_to_delete in documents_to_delete:
                uow.add_events(
                    [
                        DocumentDeleted(document_id=document.pk),
                        DeleteFiles(file_paths=self._get_document_file_paths(document_to_delete)),
                    ],
                )
            deleted = uow.document.delete(document)
            uow.commit()
        return deleted

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
        if document_type:
            self._document_type_service.find_by_id_for_tenant(document_type_id=document_type, tenant_id=tenant)

        document_creator = DocumentCreatorFactory.get_creator(file_name)

        blob_name = self._blob_service.upload(
            path=file_name, content=file_content, replace_if_exists=self.REPLACE_FILE_CONTENT_IF_EXISTS
        )

        document_entity = document_creator.generate_new_document(
            source=source,
            title=self._get_file_name_wo_ext(document_name) or self._get_file_name_wo_ext(file_name),
            blob_name=blob_name,
            reviewer=reviewer,
            language=language,
            engine=engine,
            document_type=document_type,
            sub_type=sub_type,
        )
        with self._uow() as uow:
            document_entity = uow.document.add(document_entity)
            if reviewer:
                uow.add_events([DocumentAssigned(document_id=document_entity.pk, user_id=reviewer.id)])

            if metadata:
                document_metadata = DocumentMetadata(
                    document_id=document_entity.pk,
                    metadata=metadata,
                )
                uow.document.upsert_document_metadata(document_metadata)

            if run_pipeline:
                self._run_pipeline(
                    document_type=document_type,
                    extract_data=extract_data,
                    document_entity=document_entity,
                    language=language,
                    engine=engine,
                    extraction_params=extraction_params,
                )

            uow.commit()

        return document_entity.pk

    def export(self, document_entity_pk: DocumentEntityPk) -> None:
        # TODO: move to corleone
        raise NotImplementedError("Export does not work. Need to move to Corleone")

    @staticmethod
    def _get_file_name_wo_ext(file_name: str) -> str:
        return os.path.splitext(file_name)[0] if file_name else None

    def extract_data(
        self,
        document_entity_pks: List[DocumentEntityPk],
        engine: Optional[str] = None,
    ) -> List[DocumentEntity]:
        with self._uow() as uow:
            document_entities = uow.document.select_for_update(document_entity_pks)
            for document_entity in document_entities:
                if document_entity.document_type == "Unknown":
                    raise DocumentExtractDataError(f" Document ({document_entity.pk}) has 'Unknown' document type.")

                document_entity.state = DocumentStateEnum.DATA_EXTRACTION
                self._reset_document_entity_data(document_entity)

            updated_documents = uow.document.batch_update(document_entities)
            uow.commit()

        for doc_entity in document_entities:  # noqa: WPS441
            self._pipeline_manager.run_step(
                document=doc_entity,
                engine=engine,
                step=PipelineStepsEnum.EXTRACTION,
                language=None,
                model_blob_path=None,  # TODO: should applied in Corleone
            )
        return updated_documents

    def get(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        with self._uow() as uow:
            document = uow.document.get(document_entity_pk)
            uow.commit()
        return document

    def get_descendants(self, document_entity_pk: DocumentEntityPk, include_containers: bool = False) -> List[DocumentEntity]:
        with self._uow() as uow:
            descendants = uow.document.get_descendants(document_entity_pk)
            uow.commit()
        return descendants

    def get_document_files(self, document_entity_pk: DocumentEntityPk) -> DocumentFilesDataObject:
        with self._uow() as uow:
            document_entity = uow.document.get(document_entity_pk)
            document_files_data_object = DocumentFilesDataObject(
                [b.blob_name for b in document_entity.files],
                document_entity.title,
            )
            uow.commit()
        return document_files_data_object

    def get_document_list(self, options: DocumentListFilterObject) -> DocumentListDataObject:
        with self._uow() as uow:
            total = uow.document.get_total_count_by_filter(options)
            documents = uow.document.get_list_by_filter(options)
            document_list = DocumentListDataObject(
                meta=ListResponseMetaDataObject(total=total, size=len(list(documents))),
                content=documents,
            )
            uow.commit()

        return document_list

    def get_brief_documents_info(self, document_pks: list[DocumentEntityPk]) -> list[dict]:
        with self._uow() as uow:
            documents = uow.document.get_main_info_by_pks(document_pks=document_pks)
            uow.commit()

        return documents

    def get_processed_images(self, document_entity_pk: DocumentEntityPk) -> DocumentFilesDataObject:
        with self._uow() as uow:
            document_entity = uow.document.get(document_entity_pk)
            uow.commit()
        if document_entity.state in {DocumentStateEnum.NEW, DocumentStateEnum.PREPROCESSING}:
            raise DocumentImagesAccessError("Document preprocess step is not completed")
        return DocumentFilesDataObject(
            [b.blob_name for b in document_entity.processing_documents],
            document_entity.title,
        )

    def identify(self, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        with self._uow() as uow:
            document_entities = uow.document.select_for_update(document_entity_pks)
            document_entities_for_update = []
            for document_entity in document_entities:
                if document_entity.state in UNACCEPTABLE_IDENTIFICATION_DOCUMENT_STATES:
                    raise DocumentNotAcceptableStateError(
                        f"Document ({document_entity.pk}) has 'Unacceptable' identification document state.",
                    )
                else:
                    document_entity.state = DocumentStateEnum.IDENTIFICATION
                    self._reset_document_entity_data(document_entity)
                    document_entities_for_update.append(document_entity)

            batch_updated_documents = uow.document.batch_update(document_entities_for_update)
            uow.commit()

        for doc_entity in document_entities:  # noqa: WPS441
            self._pipeline_manager.run_step(document=doc_entity, step=PipelineStepsEnum.IDENTIFICATION)

        return batch_updated_documents

    def remove_label(self, label_pk: LabelEntityPk, document_entity_pk: DocumentEntityPk) -> bool:
        with self._uow() as uow:
            removing_result = uow.document.remove_label(label_pk, document_entity_pk)
            uow.commit()
        return removing_result

    def get_document_metadata(self, document_entity_pk: DocumentEntityPk) -> DocumentMetadata:
        with self._uow() as uow:
            try:
                metadata = uow.document.get_document_metadata(document_entity_pk)
                uow.commit()
            except DocumentMetadataNotFoundError:
                return DocumentMetadata(document_id=document_entity_pk)
        return metadata

    def upsert_document_metadata(self, document_metadata: DocumentMetadata) -> DocumentMetadata:
        with self._uow() as uow:
            metadata = uow.document.upsert_document_metadata(document_metadata)
            uow.commit()
        return metadata

    def delete_document_metadata(self, document_metadata: DocumentMetadata) -> None:
        with self._uow() as uow:
            uow.document.delete_document_metadata(document_metadata)
            uow.commit()

    def reset_reviewer(self, document_entity_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        with self._uow() as uow:
            document_entities = uow.document.select_for_update(document_entity_pks)
            documents_for_reset_reviewer = []

            for document_entity in document_entities:
                if document_entity.reviewer is not None:
                    document_entity.reviewer = None
                    document_entity.state = DocumentStateEnum.COMPLETED
                    documents_for_reset_reviewer.append(document_entity)
                else:
                    raise DocumentReviewerError(f"Document ({document_entity.pk}) has 'No' reviewer")

            batch_response = uow.document.batch_update(documents_for_reset_reviewer)
            uow.commit()
        return batch_response

    def retry_last_step(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        with self._uow() as uow:
            document = uow.document.get(document_entity_pk)
            error_response = None

            if CanBeRetried.is_satisfied_by(document):
                if CanBeRetriedExtraction.is_satisfied_by(document):
                    self._reset_reviewer_and_set_extraction_state(document)
                    self._pipeline_manager.run_from_step(
                        document=document,
                        step=PipelineStepsEnum.EXTRACTION,
                        language=None,
                    )
                elif CanBeRetriedIdentification.is_satisfied_by(document):
                    self._clear_error_and_update_state(document, DocumentStateEnum.IDENTIFICATION)
                    self._pipeline_manager.run_from_step(
                        document=document,
                        step=PipelineStepsEnum.IDENTIFICATION,
                    )
                elif CanBeRetriedPreprocessing.is_satisfied_by(document):
                    self._clear_error_and_update_state(document, DocumentStateEnum.PREPROCESSING)
                    self._pipeline_manager.run_from_step(
                        document=document,
                        step=PipelineStepsEnum.PREPROCESS,
                    )
                else:
                    raise DocumentLastStepRetrievingError("Document error state not satisfied for retrying")
            else:
                raise DocumentLastStepRetrievingError("Document doesn't have errors")

            if error_response is not None:
                return error_response

            document = uow.document.get(document_entity_pk)
            uow.commit()
        return document

    def run_pipeline(
        self,
        document_entity_pks: List[DocumentEntityPk],
        engine: str,
        language: Optional[str] = None,
        need_extraction: bool = True,
        need_identification: bool = True,
    ) -> List[DocumentEntity]:
        with self._uow() as uow:
            documents = uow.document.find_by_pks(document_entity_pks)
            uow.commit()
        for document in documents:
            if document.state != DocumentStateEnum.NEW:
                raise DocumentStateError(f"Document ({document.pk}) has 'Incorrect' document state.")

        for doc in documents:
            self._pipeline_manager.run(
                document=doc,
                engine=engine,
                language=language,
                identify_document=need_identification,
                extract_data=need_extraction,
            )

        return documents

    def run_pipeline_from_step(
        self,
        document_entity_pks: List[DocumentEntityPk],
        step: PipelineStepsEnum,
        language: str,
        engine: Optional[str] = None,
    ) -> List[DocumentEntity]:
        with self._uow() as uow:
            documents = uow.document.find_by_pks(document_entity_pks)

            for doc in documents:
                if not CanBeChangedSpecification.is_satisfied_by(doc):
                    raise DocumentStateError(f"Document ({doc.pk}) has 'Incorrect' document state.")
            for doc_entity in documents:
                self._update_document(step, doc_entity)

            uow.commit()

        for document in documents:
            self._pipeline_manager.run_from_step(document=document, step=step, engine=engine, language=language)
        return documents

    def start_review(
        self,
        document_entity_pks: List[DocumentEntityPk],
        reviewer: Optional[Reviewer] = None,
        reassign_reviewer: bool = False,
    ) -> List[DocumentEntity]:
        with self._uow() as uow:
            document_entities = uow.document.select_for_update(document_entity_pks)
            documents_for_batch_start_review = []
            document_state_updated_events = []

            for document_entity in document_entities:
                if document_entity.state in START_REVIEW_STATES:
                    if reviewer and reassign_reviewer:
                        document_entity.assign_reviewer(reviewer)
                        uow.add_events(document_entity.pop_all_events())
                    document_entity.state = DocumentStateEnum.IN_REVIEW
                    documents_for_batch_start_review.append(document_entity)
                    document_state_updated_events.append(
                        DocumentStateUpdated(
                            document_id=document_entity.pk,
                            state=DocumentStateEnum.IN_REVIEW.value,
                            metadata=self.get_document_metadata(document_entity.pk).metadata,
                        ),
                    )
                else:
                    raise DocumentReviewStateError(
                        f"Document ({document_entity.pk}) is not in one of {START_REVIEW_STATES} state."
                    )

            batch_response = uow.document.batch_update(documents_for_batch_start_review)
            uow.add_events(document_state_updated_events)
            uow.commit()
        return batch_response

    def update(self, document_entity: DocumentEntity) -> DocumentEntityPk:
        with self._uow() as uow:
            documents = uow.document.select_for_update([document_entity.pk])
            old_document_entity = documents[0]
            old_document_entity.update(document_entity)
            updated = uow.document.update(document_entity)
            uow.add_events(
                [
                    DocumentUpdated(
                        document_id=document_entity.pk,
                        document=document_entity.asdict(),
                        metadata=self.get_document_metadata(document_entity.pk).metadata,
                    ),
                    *document_entity.pop_all_events(),
                ],
            )
            uow.commit()
        return updated.pk

    def partially_update(
        self,
        document_entity_pk: DocumentEntityPk,
        document_fields: Dict[str, Any],
    ) -> DocumentEntityPk:
        with self._uow() as uow:
            [document_entity] = uow.document.select_for_update([document_entity_pk])
            document_entity.partially_update(document_fields)
            response = uow.document.update(document_entity)
            document_metadata = self.get_document_metadata(document_entity_pk).metadata

            events = [
                DocumentFieldsUpdated(
                    document_id=document_entity_pk,
                    document_metadata=document_metadata,
                    updates=document_fields,
                ),
            ]
            if state := document_fields.get("state"):
                events.append(
                    DocumentStateUpdated(
                        document_id=document_entity_pk,
                        state=state,
                        metadata=document_metadata,
                        error_in_state=document_entity.error.in_state if document_entity.error else None,
                    ),
                )
            uow.add_events(events)

            uow.commit()
        return response.pk

    def update_priorities(self) -> None:
        with self._uow() as uow:
            document_entities = uow.document.get_list_by_filter(
                DocumentListFilterObject(per_page=PerPageOptions.FETCH_ALL_DOCS),
            )
            for document_entity in document_entities:
                document_entity.priority = self._priority_manager.get_priority(document_entity)

            uow.document.batch_update(document_entities)
            uow.commit()

    def validate(self, document_entity_pk: DocumentEntityPk) -> DocumentEntity:
        with self._uow() as uow:
            document_entities = uow.document.select_for_update([document_entity_pk])
            for document_entity in document_entities:
                document_entity.state = DocumentStateEnum.VALIDATION
                self._validation_service.send_document_to_validation(document_entity.pk)
                updated_document_entity = uow.document.update(document_entity)
            uow.commit()
        return updated_document_entity  # noqa: 441

    def _change_document_type(self, document_entity_pks: List[DocumentEntityPk], type_code: str) -> List[DocumentEntity]:
        with self._uow() as uow:
            documents = uow.document.select_for_update(document_entity_pks)
            documents_for_update = []
            for document in documents:
                if CanBeChangedSpecification.is_satisfied_by(document):
                    document.document_type = type_code
                    document.state = DocumentStateEnum.COMPLETED
                    document.reviewer = None
                    document = self._reset_document_entity_data(document)
                    uow.add_events([DocumentTypeChanged(document_id=document.pk)])
                    documents_for_update.append(document)
                else:
                    raise DocumentStateError(f"Document ({document.pk}) has 'Incorrect' document state.")

            batch_response = uow.document.batch_update(documents_for_update)
            uow.commit()
        return batch_response

    def _set_up_document_type(self, document_entity_pks: List[DocumentEntityPk], type_code: str) -> List[DocumentEntity]:
        with self._uow() as uow:
            documents = uow.document.select_for_update(document_entity_pks)
            documents_for_update = []
            for document in documents:
                if (doc_type := document.document_type) is not None:
                    raise DocumentAlreadyHasDocumentType(document.pk, doc_type)
                document.document_type = type_code
                documents_for_update.append(document)
            batch_response = uow.document.batch_update(documents_for_update)
            uow.commit()
        return batch_response

    def _get_document_file_paths(self, document: DocumentEntity) -> List[str]:
        file_paths = []

        for file in document.files:
            file_paths.append(file.blob_name)

        for preview_document in document.preview_documents:
            file_paths.append(preview_document.blob_name)
            file_paths.append(self._get_metadata_path(preview_document.blob_name))  # noqa: WPS437

        for processing_document in document.processing_documents:
            file_paths.append(processing_document.blob_name)
            file_paths.append(self._get_metadata_path(processing_document.blob_name))  # noqa: WPS437

        return file_paths

    def _delete_document_from_blob(self, document: DocumentEntity) -> None:
        with suppress(FileNotFound):
            for file in document.files:
                self._blob_service.delete(path=file.blob_name)

        for preview_document in document.preview_documents:
            with suppress(FileNotFound):
                self._blob_service.delete(path=preview_document.blob_name)

    def _run_pipeline(
        self,
        document_type: Optional[str],
        extract_data: bool,
        document_entity: DocumentEntity,
        language: str,
        engine: str,
        extraction_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        if document_type:
            need_identification = False
            if not engine:
                engine = None
        else:
            need_identification = True

        if document_entity.container_type is not None:
            with self._uow() as uow:
                document_entity.extract_attachments = extract_data
                self._pipeline_manager.run_step(document_entity, PipelineStepsEnum.PREPROCESS)
                child_documents = uow.document.get_descendants(document_entity.pk)
                for child_document in child_documents:
                    self._pipeline_manager.run(
                        document=child_document,
                        identify_document=need_identification,
                        extract_data=extract_data,
                        engine=engine,
                        language=language,
                        extraction_params=extraction_params,
                    )
                uow.commit()
        else:
            self._pipeline_manager.run(
                document=document_entity,
                identify_document=need_identification,
                extract_data=extract_data,
                engine=engine,
                language=language,
                extraction_params=extraction_params,
            )

    def _update_document(self, step: PipelineStepsEnum, document: DocumentEntity) -> None:
        if step is PipelineStepsEnum.PREPROCESS:
            # remove preview and processing images, reset type and remove extracted data
            document.preview_documents = []
            document.processing_documents = []
            document.document_type = None
            # TODO: reset in corleone
        elif step is PipelineStepsEnum.IDENTIFICATION:
            # reset type and remove extracted data
            document.document_type = None
        # remove extracted data
        with self._uow() as uow:
            uow.document.update(document)
            uow.commit()

    def _reset_reviewer_and_set_extraction_state(self, document: DocumentEntity):
        document.reviewer = None
        document.state = DocumentStateEnum.DATA_EXTRACTION
        with self._uow() as uow:
            uow.document.update(document)
            uow.commit()

    def _clear_error_and_update_state(self, document: DocumentEntity, state: DocumentStateEnum):
        document.error = None
        document.state = state
        with self._uow() as uow:
            uow.document.update(document)
            uow.commit()

    @staticmethod
    def _reset_document_entity_data(document_entity: DocumentEntity) -> DocumentEntity:
        document_entity.reviewer = None
        if document_entity.error is not None:
            document_entity.error.description = None
            document_entity.error.in_state = None

        return document_entity

    @staticmethod
    def _get_metadata_path(file_path: str) -> str:
        dir_path, filename = os.path.split(file_path)
        filename, _ = os.path.splitext(filename)

        metadata_filename = "metadata_{}.json".format(filename)
        metadata_path = os.path.join(dir_path, metadata_filename)

        return metadata_path
