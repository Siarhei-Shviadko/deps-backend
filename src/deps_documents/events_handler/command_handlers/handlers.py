import logging
import sys

from dependency_injector.wiring import Provide, inject
from deps_message_flow.commands.common import (
    CommandMessageHeaders,
    make_message_for_command,
)
from deps_message_flow.commands.consumer import (
    CommandHandlerReplyBuilder,
    CommandMessage,
)
from deps_message_flow.events.mappers import JsonMapper
from deps_message_flow.messaging.common import IMessage

from deps_documents.api.models.document.reviewer import ReviewerModel
from deps_documents.application import DocumentAccessServiceV2 as DocumentAccessService
from deps_documents.application import DocumentAccessServiceV3
from deps_documents.auth import get_current_user_organisation
from deps_documents.containers import Container
from deps_documents.domain.constants import (
    ContainerTypesEnum,
    DocumentStateEnum,
    ErrorType,
)
from deps_documents.domain.entities import (
    ContainerEmailMetadata,
    DocumentEntityPk,
    ParsingFeature,
)
from deps_documents.domain.exceptions import BusinessException
from deps_documents.domain.interfaces import IDocumentService

from .commands import (
    AssignDocumentType,
    AssignDocumentTypeReply,
    CreateDocument,
    CreateDocumentFromFile,
    CreateDocumentFromFileReply,
    CreateDocumentReply,
    DeleteBatchDocument,
    SaveBatchDocuments,
    SaveBatchDocumentsReplyBuilder,
    StartBatchProcessing,
    UnassignReviewer,
    UpdateContainerData,
    UpdateContainerDataReply,
    UpdateDocumentState,
)
from .reply_builder import ParticipantReplyBuilder
from .reply_builder_dec import send_participant_reply

_logger = logging.getLogger(__name__)

__all__ = [
    "create_document_handler",
    "update_state_handler",
    "unassign_reviewer_handler",
    "assign_document_type",
    "update_document_container_data",
    "save_batch_documents_handler",
    "start_batch_processing_handler",
    "delete_batch_document_handler",
    "create_document_from_file_handler",
]


@inject
def create_document_handler(
    command_message: CommandMessage,
    document_access_service: DocumentAccessService = Provide[Container.application.document_access],
) -> list[IMessage]:
    current_tenant = get_current_user_organisation()
    command: CreateDocument = command_message.command
    try:
        document_id = document_access_service.create_document(
            document_name=command.document_name,
            document_type=command.document_type_id,
            language=command.language,
            engine=command.engine,
            llm_type=command.llm_type,
            blob_name=command.files[0],
            tenant=current_tenant,
            reviewer=ReviewerModel.from_current_user() if command.assign_to_me else None,
            parent_id=command.parent_id,
        )
        if (metadata := command.document_metadata) is not None:
            document_access_service.save_metadata(document_id, metadata)

        return [ParticipantReplyBuilder.with_success(CreateDocumentReply(document_id))]
    except Exception as error:
        _logger.error("[create_document_handler] Error occured: %s", error, exc_info=True)
        return [ParticipantReplyBuilder.with_failure()]


@inject
def create_document_from_file_handler(
    command_message: CommandMessage[CreateDocumentFromFile],
    document_service: DocumentAccessServiceV3 = Provide[Container.application.document_access_v3],
):
    current_tenant = get_current_user_organisation()
    error_type, error_message, trace_info = None, None, None
    document_name = command_message.command.document_name

    try:
        document_id = document_service.create_document_with_existing_file(
            document_name=document_name,
            tenant_id=current_tenant,
            metadata=command_message.command.metadata,
            blob_name=command_message.command.file_path,
            document_type_id=command_message.command.document_type_id,
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
            assign_to_me=command_message.command.assigned_to_me,
            start_processing=command_message.command.start_processing,
        )

    except BusinessException as e:
        error_type, error_message, trace_info = ErrorType.BUSINESS, str(e), sys.exc_info()

    except Exception as e:
        error_type, error_message, trace_info = ErrorType.SYSTEM, str(e), sys.exc_info()

    if error_type is None:
        reply = CreateDocumentFromFileReply(document_id)
    else:
        _logger.error(
            f"Failed to create document from file `{document_name}`! \n Reason: {error_message}",
            exc_info=trace_info,
        )
        reply = CreateDocumentFromFileReply(error_type=error_type, error_message=error_message)

    return [
        CommandHandlerReplyBuilder.with_success(
            make_message_for_command(
                channel="NONE",
                payload=JsonMapper().serialize(reply),
                command_type=reply.__class__.__name__,
                reply_to="NONE",
            ),
        ),
    ]


@inject
def update_state_handler(
    command_message: CommandMessage,
    document_access_service: DocumentAccessService = Provide[Container.application.document_access],
) -> list[IMessage]:
    command: UpdateDocumentState = command_message.command
    try:
        document_access_service.update_state(
            command.document_id,
            DocumentStateEnum(command.state),
            ErrorType(command.error_type) if command.error_type else None,
            command.error_message,
        )
        return [ParticipantReplyBuilder.with_success()]
    except Exception as error:
        _logger.error("[update_state_handler] Error occured: %s", error, exc_info=True)
        return [ParticipantReplyBuilder.with_failure()]


@inject
def unassign_reviewer_handler(
    command_message: CommandMessage,
    document_access_service: DocumentAccessService = Provide[Container.application.document_access],
) -> list[IMessage]:
    command: UnassignReviewer = command_message.command
    try:
        document_access_service.unassign_reviewer(command.document_id)
        return [ParticipantReplyBuilder.with_success()]
    except Exception as error:
        _logger.error("[unassign_reviewer_handler] Error occured: %s", error, exc_info=True)
        return [ParticipantReplyBuilder.with_failure()]


@inject
@send_participant_reply(AssignDocumentTypeReply)
def assign_document_type(
    command_message: CommandMessage,
    document_service: IDocumentService = Provide[Container.domain_services_accessor.document],
) -> None:
    command: AssignDocumentType = command_message.command
    document_service.assign_type([DocumentEntityPk(command.document_id)], command.document_type_id, initial_assign=True)


@inject
@send_participant_reply(UpdateContainerDataReply)
def update_document_container_data(
    command_message: CommandMessage,
    document_service: IDocumentService = Provide[Container.domain_services_accessor.document],
) -> None:
    command: UpdateContainerData = command_message.command
    document_service.partially_update(
        document_entity_pk=DocumentEntityPk(command.document_id),
        document_fields={
            "container_type": ContainerTypesEnum(command.container_type),
            "container_metadata": ContainerEmailMetadata(**command.container_metadata),
        },
    )


@inject
def save_batch_documents_handler(
    command_message: CommandMessage["SaveBatchDocuments"],
    tenant_id: str = Provide[Container.current_user_tenant],
    document_service: DocumentAccessServiceV3 = Provide[Container.application.document_access_v3],
) -> list[IMessage]:
    command = command_message.command
    batch_id = command.batch_id
    reply_builder = SaveBatchDocumentsReplyBuilder(batch_id=batch_id)

    for file in command.files:
        file_id = file["id"]
        file_parsing_features = file["processing_params"]["parsing_features"]

        with reply_builder.with_file(file_id=file_id) as file_builder:
            try:
                document_id = document_service.create_document_with_existing_file(
                    document_name=file["name"],
                    tenant_id=tenant_id,
                    document_type_id=file["document_type_id"],
                    group_id=command.group_id,
                    blob_name=file["path"],
                    engine=file["processing_params"]["engine"],
                    language=file["processing_params"]["language"],
                    llm_type=file["processing_params"]["llm_type"],
                    assign_to_me=False,
                    parsing_features=set(map(ParsingFeature, file_parsing_features)) if file_parsing_features else None,
                    metadata=file["metadata"],
                    parent_id=None,
                    needs_unification=True,
                    needs_extraction=True,
                    needs_parsing=False,
                    start_processing=False,
                )
                file_builder.with_document_id(document_id)
            except Exception as exc:
                _logger.error(f"Exception occurred during batch {batch_id} file {file_id} document creation: {exc}")
                file_builder.with_error(exc)

    command_reply = reply_builder.build()

    return [
        CommandHandlerReplyBuilder.with_success(
            make_message_for_command(
                command_message.message.headers.get(CommandMessageHeaders.REPLY_TO),
                JsonMapper().serialize(command_reply),
                command_reply.__class__.__name__,
                "NONE",
            ),
        ),
    ]


@inject
def start_batch_processing_handler(
    command_message: CommandMessage["StartBatchProcessing"],
    tenant_id: str = Provide[Container.current_user_tenant],
    document_service: DocumentAccessServiceV3 = Provide[Container.application.document_access_v3],
) -> None:
    document_service.start_batch_processing(document_ids=command_message.command.documents, tenant_id=tenant_id)


@inject
def delete_batch_document_handler(
    command_message: CommandMessage["DeleteBatchDocument"],
    document_service: IDocumentService = Provide[Container.domain_services_accessor.document],
) -> None:
    document_service.delete(DocumentEntityPk(command_message.command.document))
