import contextlib
import logging
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Dict, List
from uuid import uuid4

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.common import (
    CommandReplyOutcome,
    ReplyMessageHeaders,
    make_message_for_command,
)
from deps_message_flow.commands.consumer import CommandHandlerReplyBuilder
from deps_message_flow.commands.consumer.command_message import CommandMessage
from deps_message_flow.events.mappers import JsonMapper
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.events.subscriber.domain_event_envelope import (
    DomainEventEnvelope,
)
from deps_object_storage import ObjectStorage

from deps_documents.application import (
    DocumentAccessServiceV3,
    DocumentTypeService,
    GroupService,
)
from deps_documents.auth import get_current_user_organisation
from deps_documents.constants import (
    DOCUMENT_COMMANDS_REPLIES_CHANNEL,
    DOCUMENTS_EXCHANGER,
)
from deps_documents.containers import Container, DomainServicesAccessor
from deps_documents.domain.constants import SAMPLE_DOCUMENTS, DocumentStateEnum
from deps_documents.domain.dtos import GroupInfo
from deps_documents.domain.entities import (
    BlobFile,
    BlobFileMetadata,
    DocumentEntity,
    DocumentEntityPk,
    DocumentMetadata,
    LabelEntityPk,
    ParsingFeature,
)
from deps_documents.domain.entities.factory import DocumentCreatorFactory
from deps_documents.domain.entities.preprocess import PreprocessResultEntity
from deps_documents.domain.events import (
    ClassifyDocument,
    DocumentClassificationCompleted,
    DocumentParsingBegan,
    DocumentParsingEnded,
    DocumentProcessingFailed,
    DocumentProcessingSucceed,
    DocumentReviewCompleted,
    ExtractData,
    GetGroupsReply,
    GroupCreated,
    GroupDeleted,
    GroupInfoUpdated,
    ImportDocument,
    ImportDocumentReply,
    SampleDocumentsCreated,
    UnknownDocumentType,
)
from deps_documents.domain.exceptions import DocumentClassificationError, NotFoundError
from deps_documents.domain.interfaces import IDocumentService, IUseCase

_logger = logging.getLogger(__name__)


@inject
def handle_processing_error(
    dee: DomainEventEnvelope,
    error: Exception,
    publisher: DomainEventPublisher = Provide[Container.domain_event_publishers.publisher],
) -> None:
    if dee.message.headers["x-retry-count"] == 3:
        publisher.publish(
            DOCUMENTS_EXCHANGER,
            str(dee.event.document_id),
            [DocumentProcessingFailed(document_id=dee.event.document_id, message=str(error))],
            headers={"ID": uuid4().hex},
        )


def error_handler(func):
    @wraps(func)
    def wrapper(dee, **kwargs):
        try:
            func(dee, **kwargs)
        except Exception as error:
            handle_processing_error(dee, error)
            raise

    return wrapper


def is_command_successful(command_message: CommandMessage) -> bool:
    return command_message.message.get_required_header(ReplyMessageHeaders.REPLY_OUTCOME) == CommandReplyOutcome.SUCCESS.name


@error_handler
@inject
def document_preprocess_began_handler(
    dee: DomainEventEnvelope,
    begin_preprocess_document: IUseCase = Provide[Container.use_cases.service_begin_preprocess_document],
) -> None:
    use_case = begin_preprocess_document
    use_case_request = use_case.Request(document_id=dee.event.document_id)  # type: ignore
    use_case.execute(use_case_request)


@error_handler
@inject
def document_preprocess_ended_handler(
    dee: DomainEventEnvelope,
    service_preprocess_document: IUseCase = Provide[Container.use_cases.service_preprocess_document],
    publisher: DomainEventPublisher = Provide[Container.domain_event_publishers.publisher],
    parsing_enabled: bool = Provide[Container.config.parsing_enabled],
) -> None:
    preprocess_entities = [build_preprocess_entity_from_dict(preprocess_dict) for preprocess_dict in dee.event.preprocess_result]

    use_case = service_preprocess_document
    use_case_request = use_case.Request(  # type: ignore
        document_id=dee.event.document_id,
        preprocess_entities=preprocess_entities,
        extract_attachments=dee.event.extract_attachments,
    )
    use_case_result = use_case.execute(use_case_request)
    document = use_case_result.value.document_entity

    if parsing_enabled:
        return

    doc_id = str(dee.event.document_id)

    if not dee.event.extract_data:
        publisher.publish(
            DOCUMENTS_EXCHANGER,
            doc_id,
            [DocumentProcessingSucceed(document_id=doc_id, document_type=document.document_type)],  # type: ignore
            headers={"ID": uuid4().hex},
        )
        return

    if dee.event.document_type is not None:
        publisher.publish(
            DOCUMENTS_EXCHANGER,
            doc_id,
            [
                ExtractData(
                    document_id=doc_id,  # type: ignore
                    extraction_params=dee.event.extraction_params,
                    engine=dee.event.engine,
                    language=dee.event.language,
                ),
            ],
            headers={"ID": uuid4().hex},
        )
    elif dee.event.identify_document:
        publisher.publish(
            DOCUMENTS_EXCHANGER,
            doc_id,
            [
                ClassifyDocument(
                    document_id=doc_id,  # type: ignore
                    engine=dee.event.engine,
                    language=dee.event.language,
                    extraction_params=dee.event.extraction_params,
                ),
            ],
            headers={"ID": uuid4().hex},
        )


@error_handler
@inject
def document_classification_started_handler(
    dee: DomainEventEnvelope,
    service_start_classification: IUseCase = Provide[Container.use_cases.service_start_classification],
) -> None:
    use_case = service_start_classification
    use_case_request = use_case.Request(document_id=str(dee.event.document_id))  # type: ignore
    use_case.execute(use_case_request)


@error_handler
@inject
def document_classification_ended_handler(
    dee: DomainEventEnvelope,
    service_classify_document: IUseCase = Provide[Container.use_cases.service_classify_document],
    publisher: DomainEventPublisher = Provide[Container.domain_event_publishers.publisher],
) -> None:
    use_case = service_classify_document

    doc_id = str(dee.event.document_id)
    use_case_request = use_case.Request(  # type: ignore
        document_id=doc_id,
        document_type=dee.event.document_type,
    )

    try:
        use_case.execute(use_case_request)
        publisher.publish(
            DOCUMENTS_EXCHANGER,
            doc_id,
            [
                ExtractData(
                    document_id=doc_id,  # type: ignore
                    engine=dee.event.engine,
                    language=dee.event.language,
                    extraction_params=dee.event.extraction_params,
                ),
            ],
            headers={"ID": uuid4().hex},
        )
    except DocumentClassificationError:
        # TODO: What should we do in case of document_type=None from classification service?
        publisher.publish(
            DOCUMENTS_EXCHANGER,
            dee.event.document_id,
            [UnknownDocumentType(document_id=dee.event.document_id)],
            headers={"ID": uuid4().hex},
        )


@error_handler
@inject
def document_extraction_began_handler(
    dee: DomainEventEnvelope,
    service_begin_extraction: IUseCase = Provide[Container.use_cases.service_begin_extraction],
    parsing_enabled: bool = Provide[Container.config.parsing_enabled],
) -> None:
    logging.info(dee.message.headers)
    if not parsing_enabled:
        use_case = service_begin_extraction
        use_case_request = use_case.Request(document_id=dee.event.document_id, engine=dee.event.engine)  # type: ignore
        use_case.execute(use_case_request)


@error_handler
@inject
def document_extraction_ended_handler(
    dee: DomainEventEnvelope,
    publisher: DomainEventPublisher = Provide[Container.domain_event_publishers.publisher],
    document_service: IDocumentService = Provide[DomainServicesAccessor.document],
    auto_validation_enabled: bool = Provide[Container.config.auto_validation_enabled],
) -> None:
    # TODO Aliaksei Yurkevich 20.12.2022: Fix types in events
    document_id = str(dee.event.document_id)
    if auto_validation_enabled:
        document_service.validate(document_id)  # type: ignore
    else:
        document = document_service.get(document_entity_pk=document_id)  # type: ignore
        publisher.publish(
            DOCUMENTS_EXCHANGER,
            str(dee.event.document_id),
            [
                DocumentProcessingSucceed(
                    document_id=dee.event.document_id,
                    document_type=document.document_type,
                ),
            ],
            headers={"ID": uuid4().hex},
        )


def document_imported_handler(
    dee: DomainEventEnvelope,
    engine: str = "TESSERACT",
) -> None:
    _import_document_into_deps(
        document_name=dee.event.document_name,
        document_type=dee.event.document_type,
        document_file_paths=dee.event.files_paths,
        document_metadata=dee.event.document_metadata,
        need_identification=dee.event.need_identification,
        engine=engine,
    )


@error_handler
@inject
def document_processing_succeed_handler(
    dee: DomainEventEnvelope,
    service_succeeded: IUseCase = Provide[Container.use_cases.service_succeeded],
) -> None:
    use_case = service_succeeded
    use_case_request = use_case.Request(document_id=dee.event.document_id)  # type: ignore

    use_case.execute(use_case_request)


@inject
def document_processing_failed_handler(
    dee: DomainEventEnvelope,
    service_failed: IUseCase = Provide[Container.use_cases.service_failed],
) -> None:
    use_case = service_failed
    use_case_request = use_case.Request(document_id=dee.event.document_id)  # type: ignore
    use_case.execute(use_case_request)


@inject
def organisation_created_handler(
    dee: DomainEventEnvelope,
    document_service: IDocumentService = Provide[DomainServicesAccessor.document],
    blob_service: ObjectStorage = Provide[Container.services.object_storage],
    publisher: DomainEventPublisher = Provide[Container.domain_event_publishers.publisher],
) -> None:
    if not dee.event.personal:
        return

    documents = []

    for sample_document in SAMPLE_DOCUMENTS:
        document_creator = DocumentCreatorFactory.get_creator(sample_document["file_name"])  # type: ignore

        with open(sample_document["file_path"], "r+b") as document_file:  # type: ignore
            blob_name = blob_service.upload(
                path=sample_document["file_name"],  # type: ignore
                content=document_file.read(),
                replace_if_exists=True,
            )

        document_entity = document_creator.generate_new_document(
            title=sample_document["file_name"],
            blob_name=blob_name,
            language=sample_document["language"],
            engine=sample_document["engine"],
            state=DocumentStateEnum.COMPLETED,
            source=None,
            document_type=None,
            sub_type=None,
        )

        document_pk = document_service.create(document_entity)

        documents.append({"sample_id": sample_document["sample_id"], "document_id": int(document_pk), "files": [blob_name]})

    publisher.publish(
        DOCUMENTS_EXCHANGER,
        "None",
        [SampleDocumentsCreated(documents=documents)],
        headers={"ID": uuid4().hex},
    )


@inject
def sample_documents_preprocessed_event_handler(
    dee: DomainEventEnvelope,
    service_preprocess_document: IUseCase = Provide[Container.use_cases.service_preprocess_document],
):
    for document in dee.event.documents:
        preprocess_entities = [
            build_preprocess_entity_from_dict(preprocess_dict) for preprocess_dict in document["preprocess_result"]
        ]

        use_case = service_preprocess_document
        use_case_request = use_case.Request(  # type: ignore
            document_id=DocumentEntityPk(str(document["document_id"])),
            preprocess_entities=preprocess_entities,
            extract_attachments=False,
        )
        use_case.execute(use_case_request)


@inject
def delete_document_handler(
    command_message: CommandMessage,
    document_service: IDocumentService = Provide[DomainServicesAccessor.document],
):
    document_service.delete(DocumentEntityPk(command_message.command.document_id))


@inject
def document_parsing_began_handler(
    dee: DomainEventEnvelope[DocumentParsingBegan],
    service_begin_extraction: IUseCase = Provide[Container.use_cases.service_begin_extraction],
) -> None:
    use_case = service_begin_extraction
    use_case_request = use_case.Request(document_id=dee.event.document_id, engine="")  # type: ignore
    use_case.execute(use_case_request)


@inject
def document_parsing_ended_handler(
    dee: DomainEventEnvelope[DocumentParsingEnded],
    document_service: IDocumentService = Provide[Container.domain_services_accessor.document],
    publisher: DomainEventPublisher = Provide[Container.domain_event_publishers.publisher],
) -> None:
    doc_id = str(dee.event.document_id)
    if dee.event.extract_data and dee.event.document_type:
        publisher.publish(
            DOCUMENTS_EXCHANGER,
            doc_id,
            [
                ExtractData(
                    document_id=doc_id,  # type: ignore
                    extraction_params=dee.event.extraction_params,
                    engine=dee.event.engine,
                ),
            ],
        )
    else:
        document = document_service.get(document_entity_pk=doc_id)  # type: ignore
        publisher.publish(
            DOCUMENTS_EXCHANGER,
            doc_id,
            [
                DocumentProcessingSucceed(
                    document_id=doc_id,  # type: ignore
                    document_type=document.document_type,
                ),
            ],
        )


def is_command_was_successful(command_message) -> bool:
    return command_message.message.get_required_header(ReplyMessageHeaders.REPLY_OUTCOME) == CommandReplyOutcome.SUCCESS.name


@inject
def validation_reply_handler(
    command_message: CommandMessage,
    document_service: IDocumentService = Provide[DomainServicesAccessor.document],
    publisher: DomainEventPublisher = Provide[Container.domain_event_publishers.publisher],
    service_succeeded: IUseCase = Provide[Container.use_cases.service_succeeded],
    service_review_document: IUseCase = Provide[Container.use_cases.service_review_document],
    service_failed: IUseCase = Provide[Container.use_cases.service_failed],
) -> None:
    document_id = command_message.command.document_id
    if is_command_was_successful(command_message):
        if command_message.command.is_valid:
            use_case = service_succeeded
            publisher.publish(
                DOCUMENTS_EXCHANGER,
                str(document_id),
                [
                    DocumentReviewCompleted(
                        document_id=document_id,
                        document_metadata=document_service.get_document_metadata(document_id).metadata,
                    ),
                ],
            )
            use_case_request = use_case.Request(document_id=document_id, unassign_reviewer=True)  # type: ignore
        else:
            use_case = service_review_document
            use_case_request = use_case.Request(document_id=document_id)  # type: ignore
    else:
        service_failed.execute(service_failed.Request(document_id=document_id))

    use_case.execute(use_case_request)


@inject
def import_document_handler(
    command_message: CommandMessage[ImportDocument],
    document_service: DocumentAccessServiceV3 = Provide[Container.application.document_access_v3],
):
    current_tenant = get_current_user_organisation()

    try:
        document_id = document_service.create_document_with_existing_file(
            document_name=command_message.command.document_name,
            tenant_id=current_tenant,
            metadata=command_message.command.document_metadata,
            blob_name=command_message.command.file_path,
            document_type_id=command_message.command.document_type,
            needs_unification=command_message.command.invoke_unifier,
            needs_extraction=command_message.command.invoke_extraction,
            needs_parsing=bool(command_message.command.parsing_features),
            parsing_features={ParsingFeature(feature) for feature in command_message.command.parsing_features}
            if command_message.command.parsing_features
            else None,
            language=command_message.command.language,
            engine=command_message.command.engine,
            llm_type=command_message.command.llm_type,
            group_id=command_message.command.group_id,
            assign_to_me=True,
            label_ids=[LabelEntityPk(label) for label in command_message.command.label_ids]
            if command_message.command.label_ids
            else None,
        )
    except Exception as exc:
        _logger.error(f"Import document command {command_message.message_id} failed with: {str(exc)}")
        command_reply = ImportDocumentReply(
            document_id=None,
            document_metadata=command_message.command.document_metadata,
        )

        message_reply = CommandHandlerReplyBuilder.with_failure(
            make_message_for_command(
                DOCUMENT_COMMANDS_REPLIES_CHANNEL,
                JsonMapper().serialize(command_reply),
                command_reply.__class__.__name__,
                "NONE",
            ),
        )

        return [message_reply]

    command_reply = ImportDocumentReply(
        document_id=document_id,
        document_metadata=command_message.command.document_metadata,
    )

    message_reply = CommandHandlerReplyBuilder.with_success(
        make_message_for_command(
            DOCUMENT_COMMANDS_REPLIES_CHANNEL,
            JsonMapper().serialize(command_reply),
            command_reply.__class__.__name__,
            "NONE",
        ),
    )

    return [message_reply]


def _build_blob_file_from_dict(blob_file: Dict[str, Any]) -> BlobFile:
    # TODO: refactor BlobFile to support multiple type meta
    metadata = blob_file.get("meta", {})
    if metadata:
        metadata = BlobFileMetadata(width=metadata["width"], height=metadata["height"])
    return BlobFile(blob_name=blob_file["blob_name"], metadata=metadata)


def build_preprocess_entity_from_dict(preprocess_dict: Dict[str, Any]) -> PreprocessResultEntity:
    return PreprocessResultEntity(
        entity_type=preprocess_dict.get("entity_type"),
        preview=[_build_blob_file_from_dict(file) for file in preprocess_dict.get("preview", []) if file.get("blob_name")],
        processing=[_build_blob_file_from_dict(file) for file in preprocess_dict.get("processing", []) if file.get("blob_name")],
        meta=preprocess_dict.get("meta"),
    )


@inject
def _import_document_into_deps(
    document_name: str,
    document_type: str,
    document_file_paths: List[str],
    document_metadata: dict[str, Any],
    need_identification: bool,
    engine: str,
    document_service: IDocumentService = Provide[DomainServicesAccessor.document],
) -> DocumentEntityPk:
    blob_files = [BlobFile(blob_name=file_path) for file_path in document_file_paths]
    document_entity = DocumentEntity(
        pk=None,
        title=document_name,
        state=DocumentStateEnum.NEW,
        files=blob_files,
        document_type=document_type,
        date=datetime.now(tz=timezone.utc),
    )
    document_pk = document_service.create(document_entity)
    document_metadata_entity = DocumentMetadata(
        document_id=document_pk,
        metadata=document_metadata,
    )
    document_service.upsert_document_metadata(document_metadata_entity)
    document_service.run_pipeline([document_pk], engine=engine, need_identification=need_identification)

    return document_pk


@inject
def document_type_created_handler(
    dee: DomainEventEnvelope,
    document_type_service: DocumentTypeService = Provide[Container.application.document_type],
) -> None:
    document_type_service.save_document_type(
        document_type_id=dee.event.document_type,
        tenant_id=dee.event.tenant,
        name=dee.event.name,
    )


@inject
def document_type_deleted_handler(
    dee: DomainEventEnvelope,
    document_type_service: DocumentTypeService = Provide[Container.application.document_type],
) -> None:
    with contextlib.suppress(NotFoundError):
        document_type_service.delete_document_type(document_type_id=dee.event.document_type, tenant_id=dee.event.tenant)


@inject
def get_document_types_reply_handler(
    command_message: CommandMessage,
    document_type_service: DocumentTypeService = Provide[Container.application.document_type],
) -> None:
    if is_command_successful(command_message):
        document_types = command_message.command.document_types
        document_type_service.save_document_types(document_types)
        _logger.info("Document types updated successfully")
    else:
        _logger.error(f"Failed to get document types. Command headers: {command_message.message.headers}")


@error_handler
@inject
def document_classification_completed_handler(
    dee: DomainEventEnvelope[DocumentClassificationCompleted],
    document_service: DocumentAccessServiceV3 = Provide[Container.application.document_access_v3],
) -> None:
    event = dee.event

    document_service.assign_document_type(
        tenant_id=event.tenant_id,
        document_id=event.document_id,
        document_type_id=event.document_type_id,
    )


@inject
def get_groups_reply_handler(
    command_message: CommandMessage[GetGroupsReply],
    group_service: GroupService = Provide[Container.application.group],
) -> None:
    if is_command_successful(command_message):
        group_service.save_groups(
            [
                GroupInfo(
                    id=group["id"],
                    tenant_id=group["tenant_id"],
                    name=group["name"],
                    is_deleted=group["is_deleted"],
                )
                for group in command_message.command.groups
            ],
        )
        _logger.info("Groups updated successfully")
    else:
        _logger.error(f"Failed to get groups. Command headers: {command_message.message.headers}")


@inject
def group_created_handler(
    dee: DomainEventEnvelope[GroupCreated],
    group_service: GroupService = Provide[Container.application.group],
) -> None:
    group_service.save_group(group_id=dee.event.id, tenant_id=dee.event.tenant_id, name=dee.event.name)


@inject
def group_deleted_handler(
    dee: DomainEventEnvelope[GroupDeleted],
    group_service: GroupService = Provide[Container.application.group],
) -> None:
    group_service.mark_deleted(group_id=dee.event.id, tenant_id=dee.event.tenant_id)


@inject
def group_info_updated_handler(
    dee: DomainEventEnvelope[GroupInfoUpdated],
    group_service: GroupService = Provide[Container.application.group],
) -> None:
    group_service.save_group(group_id=dee.event.id, tenant_id=dee.event.tenant_id, name=dee.event.name)
