import logging
import os
from typing import Any, Callable, Optional
from uuid import uuid4

from deps_message_flow.commands.producer import CommandProducer
from deps_object_storage import ObjectStorage

from deps_documents.constants import (
    CLASSIFICATION_COMMANDS_CHANNEL,
    DOCUMENT_COMMANDS_REPLIES_CHANNEL,
    WORKFLOW_MANAGER_COMMANDS_CHANNEL,
)
from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.entities import (
    DocumentEntity,
    DocumentEntityPk,
    DocumentMetadata,
    GroupEntity,
    LabelEntityPk,
    ParsingFeature,
)
from deps_documents.domain.events.events import DocumentTypeAssignedToDocument
from deps_documents.domain.exceptions import DocumentMetadataNotFoundError
from deps_documents.domain.interfaces import IDocumentUnitOfWork
from deps_documents.domain.model import (
    ClassifyDocument,
    DocumentCreatorFactory,
    ProcessDocument,
)
from deps_documents.infrastructure.access_management.context_vars import user

__all__ = ["DocumentService"]


class DocumentService:
    REPLACE_FILE_CONTENT_IF_EXISTS = True

    def __init__(
        self,
        uow: Callable[..., IDocumentUnitOfWork],
        file_storage: ObjectStorage,
        command_producer: CommandProducer,
    ):
        self._uow = uow
        self._file_storage = file_storage
        self._command_producer = command_producer

        self._logger = logging.getLogger(self.__class__.__name__)

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
        metadata: dict[str, Any] = None,
        parent_id: Optional[str] = None,
        needs_unification: bool = False,
        needs_extraction: bool = False,
        needs_parsing: bool = False,
        label_ids: Optional[list[LabelEntityPk]] = None,
    ) -> DocumentEntity:
        with self._uow() as uow:
            if document_type_id:
                uow.document_type.find_by_id_for_tenant(
                    document_type_id=document_type_id,
                    tenant_id=tenant_id,
                )
            group = (
                uow.group.find_by_id_for_tenant(
                    group_id=group_id,
                    tenant_id=tenant_id,
                )
                if group_id is not None
                else None
            )

            document = self._create_document(
                uow=uow,
                title=document_name,
                blob_name=blob_name,
                parent_id=parent_id,
                document_type_id=document_type_id,
                group=group,
                engine=engine,
                language=language,
                llm_type=llm_type,
                metadata=metadata,
                parsing_features=parsing_features,
                needs_unification=needs_unification,
                needs_extraction=needs_extraction,
                needs_parsing=needs_parsing,
                assign_to_me=assign_to_me,
                label_ids=label_ids,
            )

            uow.commit()

        self._logger.info(f"Document with name `{document_name}` created: id = {document.pk}.")

        return document

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
    ) -> DocumentEntity:
        with self._uow() as uow:
            if document_type_id:
                uow.document_type.find_by_id_for_tenant(
                    document_type_id=document_type_id,
                    tenant_id=tenant_id,
                )
            group = (
                uow.group.find_by_id_for_tenant(
                    group_id=group_id,
                    tenant_id=tenant_id,
                )
                if group_id is not None
                else None
            )
            _, file_extension = os.path.splitext(file_name)

            blob_name = self._file_storage.upload(
                path=uuid4().hex + file_extension,
                content=file_content,
                replace_if_exists=self.REPLACE_FILE_CONTENT_IF_EXISTS,
            )

            document = self._create_document(
                uow=uow,
                title=document_name,
                blob_name=blob_name,
                parent_id=parent_id,
                document_type_id=document_type_id,
                group=group,
                engine=engine,
                language=language,
                llm_type=llm_type,
                metadata=metadata,
                parsing_features=parsing_features,
                needs_unification=needs_unification,
                needs_extraction=needs_extraction,
                needs_parsing=needs_parsing,
                needs_validation=needs_validation,
                needs_review=needs_review,
                needs_output_exporting=needs_output_exporting,
                assign_to_me=assign_to_me,
                label_ids=label_ids,
            )

            uow.commit()

        self._logger.info(f"Document with name `{document_name}` created: id = {document.pk}.")

        return document

    def assign_document_type(self, tenant_id: str, document_id: str, document_type_id: Optional[str]) -> None:
        with self._uow() as uow:
            document = uow.document.get(DocumentEntityPk(document_id))

            if document_type_id is not None:
                # checking that document type exists
                uow.document_type.find_by_id_for_tenant(
                    document_type_id=document_type_id,
                    tenant_id=tenant_id,
                )
                document.document_type = document_type_id

                uow.add_events(
                    [
                        DocumentTypeAssignedToDocument(
                            document_id=document_id,
                            document_type_id=document_type_id,
                            metadata=self._get_document_metadata(DocumentEntityPk(document_id)).metadata,
                        ),
                    ],
                )

            uow.add_events(document.pop_all_events())
            uow.document.update(document)

            self._start_document_processing(
                document_id=document.pk,
                tenant_id=tenant_id,
                files=document.blob_names,
                document_type_id=document_type_id,
                engine=document.engine,
                language=document.language,
                llm_type=document.llm_type,
                parsing_features=document.parsing_features,
                needs_unification=document.needs_unification,
                needs_extraction=document.needs_extraction,
                needs_parsing=document.needs_parsing,
                needs_validation=document.needs_validation,
                needs_review=document.needs_review,
                needs_output_exporting=document.needs_output_exporting,
            )

            uow.commit()

        self._logger.info(f"Document type {document_type_id} assigned to the document {document_id}. ")

    def start_batch_processing(self, document_ids: list[str], tenant_id: str) -> None:
        with self._uow() as uow:
            documents = uow.document.find_by_pks([DocumentEntityPk(id_) for id_ in document_ids])

        for document in documents:
            self.initiate_document_processing(
                document=document,
                tenant_id=tenant_id,
                document_type_id=document.document_type,
                group_id=(g := document.group) and g.id,
                engine=document.engine,
                language=document.language,
                llm_type=document.llm_type,
                parsing_features=document.parsing_features,
                needs_unification=document.needs_unification,
                needs_extraction=document.needs_extraction,
                needs_parsing=document.needs_parsing,
            )

    def initiate_document_processing(
        self,
        document: DocumentEntity,
        tenant_id: str,
        document_type_id: Optional[str],
        group_id: Optional[str],
        engine: Optional[str],
        language: Optional[str],
        llm_type: Optional[str],
        parsing_features: Optional[set[ParsingFeature]] = None,
        needs_unification: bool = False,
        needs_extraction: bool = False,
        needs_parsing: Optional[bool] = None,
        needs_validation: Optional[bool] = None,
        needs_review: Optional[str] = None,
        needs_output_exporting: Optional[bool] = None,
    ) -> None:
        if not document_type_id and group_id:
            self._start_document_classification(
                document_id=document.pk,
                tenant_id=tenant_id,
                group_id=group_id,
                files=document.blob_names,
                engine=engine,
                language=language,
                parsing_features=parsing_features,
            )

        else:
            self._start_document_processing(
                document_id=document.pk,
                tenant_id=tenant_id,
                files=document.blob_names,
                document_type_id=document_type_id,
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

    def _create_document(
        self,
        uow: IDocumentUnitOfWork,
        title: str,
        blob_name: str,
        parent_id: Optional[str] = None,
        document_type_id: Optional[str] = None,
        group: Optional[GroupEntity] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        metadata: dict[str, Any] = None,
        parsing_features: Optional[set[ParsingFeature]] = None,
        needs_unification: bool = False,
        needs_extraction: bool = False,
        needs_parsing: Optional[bool] = None,
        needs_validation: Optional[bool] = None,
        needs_review: Optional[str] = None,
        needs_output_exporting: Optional[bool] = None,
        assign_to_me: bool = False,
        label_ids: Optional[list[LabelEntityPk]] = None,
    ) -> DocumentEntity:
        document_creator = DocumentCreatorFactory.get_creator(blob_name)
        document = document_creator.generate_new_document(
            title=title,
            blob_name=blob_name,
            document_type_id=document_type_id,
            group=group,
            parent_id=parent_id,
            language=language,
            engine=engine,
            llm_type=llm_type,
            state=DocumentStateEnum.NEW,
            reviewer_info=user.get(None),
            assign_to_me=assign_to_me,
            parsing_features=parsing_features,
            needs_unification=needs_unification,
            needs_extraction=needs_extraction,
            needs_parsing=needs_parsing,
            needs_validation=needs_validation,
            needs_review=needs_review,
            needs_output_exporting=needs_output_exporting,
        )

        document = uow.document.add(entity=document)

        if metadata:
            document_metadata = DocumentMetadata(
                document_id=document.pk,
                metadata=metadata,
            )
            uow.document.upsert_document_metadata(document_metadata)

        if label_ids:
            uow.document.add_bulk_labels(label_ids, document.pk)

        return document

    def _start_document_classification(
        self,
        document_id: str,
        tenant_id: str,
        group_id: str,
        files: list[str],
        engine: Optional[str] = None,
        language: Optional[str] = None,
        parsing_features: Optional[set[ParsingFeature]] = None,
    ) -> None:
        self._command_producer.send(
            CLASSIFICATION_COMMANDS_CHANNEL,
            ClassifyDocument(
                document_id=document_id,
                tenant_id=tenant_id,
                group_id=group_id,
                files=files,
                engine=engine,
                language=language,
                parsing_features=list(parsing_features) if parsing_features else None,
            ),
            DOCUMENT_COMMANDS_REPLIES_CHANNEL,
        )

    def _start_document_processing(
        self,
        document_id: str,
        tenant_id: str,
        files: list[str],
        document_type_id: Optional[str] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        llm_type: Optional[str] = None,
        parsing_features: Optional[set[ParsingFeature]] = None,
        needs_unification: bool = True,
        needs_extraction: bool = True,
        needs_parsing: Optional[bool] = None,
        needs_validation: Optional[bool] = None,
        needs_review: Optional[str] = None,
        needs_output_exporting: Optional[bool] = None,
    ) -> None:
        self._command_producer.send(
            WORKFLOW_MANAGER_COMMANDS_CHANNEL,
            ProcessDocument(
                document_id=document_id,
                tenant_id=tenant_id,
                files=files,
                document_type_id=document_type_id,
                engine=engine,
                language=language,
                llm_type=llm_type,
                parsing_features=sorted(parsing_features) if parsing_features else None,
                needs_unification=needs_unification,
                needs_extraction=needs_extraction,
                needs_parsing=needs_parsing,
                needs_validation=needs_validation,
                needs_review=needs_review,
                needs_output_exporting=needs_output_exporting,
            ),
            DOCUMENT_COMMANDS_REPLIES_CHANNEL,
        )

    def _get_document_metadata(self, document_entity_pk: DocumentEntityPk) -> DocumentMetadata:
        with self._uow() as uow:
            try:
                metadata = uow.document.get_document_metadata(document_entity_pk)
                uow.commit()
            except DocumentMetadataNotFoundError:
                return DocumentMetadata(document_id=document_entity_pk)

        return metadata
