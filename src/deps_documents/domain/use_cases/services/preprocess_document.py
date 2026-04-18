import os
from dataclasses import dataclass, field
from typing import Any, Dict, List

from deps_object_storage import ObjectStorage

from deps_documents.domain.constants import ContainerTypesEnum, PipelineStepsEnum
from deps_documents.domain.dtos import UseCaseResponseObject
from deps_documents.domain.entities import (
    ContainerEmailMetadata,
    DocumentEntity,
    DocumentEntityPk,
)
from deps_documents.domain.entities.factory import DocumentCreatorFactory
from deps_documents.domain.entities.preprocess import PreprocessResultEntity
from deps_documents.domain.exceptions import DocumentNotFoundError
from deps_documents.domain.interfaces import (
    IDocumentService,
    IPipelineManagerService,
    IUseCase,
)


@dataclass
class RequestObject:
    document_id: DocumentEntityPk
    extract_attachments: bool = True
    preprocess_entities: List[PreprocessResultEntity] = field(default_factory=list)


@dataclass
class ResponseObject:
    document_entity: DocumentEntity


class AcceptPreprocessResultUseCase(IUseCase[RequestObject, ResponseObject]):
    Request = RequestObject

    def __init__(
        self,
        document_service: IDocumentService,
        blob_service: ObjectStorage,
        pipeline_manager: IPipelineManagerService,
    ) -> None:
        self._blob_service = blob_service
        self._pipeline_manager = pipeline_manager
        self._document_service = document_service

    def execute(self, request_object: RequestObject):
        try:
            # TODO: make better processor for different preprocess responses. Declare interface
            # This condition made for support email which could only be one document
            if (
                len(request_object.preprocess_entities)
                and request_object.preprocess_entities[0].entity_type == ContainerTypesEnum.EMAIL.value
            ):
                response = self._process_email(request_object)
            else:
                response = self._process_request(request_object)
        except DocumentNotFoundError as e:
            return UseCaseResponseObject[ResponseObject].build_error(e)

        return UseCaseResponseObject[ResponseObject].build_success(response)

    def _process_request(self, request_object: RequestObject) -> ResponseObject:
        document_entity = self._document_service.get(request_object.document_id)

        preview_entities, processing_entities = [], []
        for file in request_object.preprocess_entities:
            preview_entities.extend(file.preview)
            processing_entities.extend(file.processing)

        document_entity.preview_documents = preview_entities
        document_entity.processing_documents = processing_entities

        document_entity.container_type = None
        document_entity.container_metadata = None

        self._document_service.update(document_entity)
        return ResponseObject(document_entity=document_entity)

    def _process_email(self, request_object: RequestObject) -> ResponseObject:
        document_entity_parent = self._document_service.get(request_object.document_id)

        # For now we're supporting only 1 email per document
        # We can't support multiple emails as 1 doc for now
        if len(request_object.preprocess_entities) == 1:
            preprocess_entity = request_object.preprocess_entities[0]
            if preprocess_entity.meta:
                email_meta = self._load_email_meta(preprocess_entity.meta)
                document_entity_parent.container_type = ContainerTypesEnum.EMAIL
                document_entity_parent.container_metadata = email_meta
                self._document_service.update(document_entity_parent)

            child_documents = []
            for attachment_file in preprocess_entity.processing:
                file_name = os.path.basename(attachment_file.blob_name)
                orig_title = preprocess_entity.meta["attached_titles"][file_name] if preprocess_entity.meta else file_name
                document_creator = DocumentCreatorFactory.get_creator(file_name)
                document_entity = document_creator.generate_new_document(
                    source=document_entity_parent.source_code,
                    title=self._get_file_name_wo_ext(orig_title),
                    blob_name=attachment_file.blob_name,
                    reviewer=document_entity_parent.reviewer,
                    language=document_entity_parent.language,
                    engine=None,
                    document_type=document_entity_parent.document_type,
                    parent_id=document_entity_parent.pk,
                    sub_type=document_entity_parent.sub_type,
                )
                document_entity.pk = self._document_service.create(document_entity)
                child_documents.append(document_entity)
                self._run_pipeline(document_entity, request_object.extract_attachments)
        return ResponseObject(document_entity=document_entity_parent)

    def _run_pipeline(self, document_entity: DocumentEntity, extract_data: bool = True) -> None:
        engine = None
        need_identification = True
        if document_entity.document_type:
            need_identification = False

        if document_entity.container_type is not None:
            self._pipeline_manager.run_step(document_entity, PipelineStepsEnum.PREPROCESS)
            child_documents = self._document_service.get_descendants(document_entity.pk)
            for child_document in child_documents:
                self._pipeline_manager.run(
                    document=child_document,
                    identify_document=need_identification,
                    extract_data=extract_data,
                    engine=engine,
                )
        else:
            self._pipeline_manager.run(
                document=document_entity,
                identify_document=need_identification,
                extract_data=extract_data,
                engine=engine,
            )

    @staticmethod
    def _load_email_meta(preprocess_entity_meta: Dict[str, Any]) -> ContainerEmailMetadata:
        return ContainerEmailMetadata(
            subject=preprocess_entity_meta.get("subject"),
            sender=preprocess_entity_meta.get("sender"),
            recipients=preprocess_entity_meta.get("recipients"),
            cc=preprocess_entity_meta.get("cc"),
            body=preprocess_entity_meta.get("body"),
            date=preprocess_entity_meta.get("date"),
        )

    @staticmethod
    def _get_file_name_wo_ext(file_name: str) -> str:
        return os.path.splitext(file_name)[0] if file_name else None
