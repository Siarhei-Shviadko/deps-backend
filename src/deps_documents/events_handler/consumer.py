import logging

from deps_message_flow.commands.consumer import (
    CommandDispatcher,
    CommandHandlersBuilder,
)
from deps_message_flow.events.subscriber import (
    DomainEventDispatcher,
    DomainEventHandlersBuilder,
)
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer

from deps_documents.constants import (
    COMMANDS_QUEUE,
    DOCUMENT_COMMANDS_CHANNEL,
    DOCUMENT_COMMANDS_REPLIES_CHANNEL,
    DOCUMENT_TYPE_EXCHANGER,
    DOCUMENTS_EXCHANGER,
    GROUP_EXCHANGER,
    QUEUE,
    SERVICE_CHANNEL,
    VALIDATION_COMMANDS_REPLIES_CHANNEL,
)
from deps_documents.domain.events import (
    ClassificationEnded,
    ClassificationStarted,
    DeleteDocument,
    DocumentClassificationCompleted,
    DocumentExtracted,
    DocumentExtractionBegan,
    DocumentImported,
    DocumentParsingBegan,
    DocumentParsingEnded,
    DocumentPreprocessBegan,
    DocumentPreprocessEnded,
    DocumentProcessingFailed,
    DocumentProcessingSucceed,
    DocumentTypeCreated,
    DocumentTypeDeleted,
    GetDocumentTypesReply,
    GetGroupsReply,
    GroupCreated,
    GroupDeleted,
    GroupInfoUpdated,
    ImportDocument,
    OrganisationCreated,
    SampleDocumentsPreprocessed,
    ValidationReply,
)

_logger = logging.getLogger(__name__)


def make_consumer(consumer: IMessageConsumer, producer: IMessageProducer, parsing_enabled: bool = False) -> IMessageConsumer:
    from deps_documents.events_handler.command_handlers import (  # noqa: WPS433
        AssignDocumentType,
        CreateDocument,
        CreateDocumentFromFile,
        DeleteBatchDocument,
        SaveBatchDocuments,
        StartBatchProcessing,
        UnassignReviewer,
        UpdateContainerData,
        UpdateDocumentState,
        assign_document_type,
        create_document_from_file_handler,
        create_document_handler,
        delete_batch_document_handler,
        save_batch_documents_handler,
        start_batch_processing_handler,
        unassign_reviewer_handler,
        update_document_container_data,
        update_state_handler,
    )
    from deps_documents.events_handler.handlers import (  # noqa: WPS433
        delete_document_handler,
        document_classification_completed_handler,
        document_classification_ended_handler,
        document_classification_started_handler,
        document_extraction_began_handler,
        document_extraction_ended_handler,
        document_imported_handler,
        document_parsing_began_handler,
        document_parsing_ended_handler,
        document_preprocess_began_handler,
        document_preprocess_ended_handler,
        document_processing_failed_handler,
        document_processing_succeed_handler,
        document_type_created_handler,
        document_type_deleted_handler,
        get_document_types_reply_handler,
        get_groups_reply_handler,
        group_created_handler,
        group_deleted_handler,
        group_info_updated_handler,
        import_document_handler,
        organisation_created_handler,
        sample_documents_preprocessed_event_handler,
        validation_reply_handler,
    )

    _logger.info("Start consuming...")

    events_handlers_builder = (
        DomainEventHandlersBuilder.for_aggregate_type(DOCUMENTS_EXCHANGER)
        .on_event(DocumentImported, document_imported_handler)
        .on_event(DocumentPreprocessBegan, document_preprocess_began_handler)
        .on_event(DocumentPreprocessEnded, document_preprocess_ended_handler)
        .on_event(ClassificationStarted, document_classification_started_handler)
        .on_event(ClassificationEnded, document_classification_ended_handler)
        .on_event(DocumentExtractionBegan, document_extraction_began_handler)
        .on_event(DocumentExtracted, document_extraction_ended_handler)
        .on_event(DocumentProcessingSucceed, document_processing_succeed_handler)
        .on_event(DocumentProcessingFailed, document_processing_failed_handler)
        .on_event(OrganisationCreated, organisation_created_handler)
        .on_event(SampleDocumentsPreprocessed, sample_documents_preprocessed_event_handler)
        .on_event(DocumentTypeCreated, document_type_created_handler)
        .on_event(DocumentTypeDeleted, document_type_deleted_handler)
        .on_event(DocumentClassificationCompleted, document_classification_completed_handler)
        .and_for_aggregate_type(DOCUMENT_TYPE_EXCHANGER)
        .on_event(DocumentTypeCreated, document_type_created_handler)
        .on_event(DocumentTypeDeleted, document_type_deleted_handler)
        .and_for_aggregate_type(GROUP_EXCHANGER)
        .on_event(GroupCreated, group_created_handler)
        .on_event(GroupDeleted, group_deleted_handler)
        .on_event(GroupInfoUpdated, group_info_updated_handler)
        .for_queue(QUEUE)
    )
    if parsing_enabled:
        (
            events_handlers_builder.and_for_aggregate_type(DOCUMENTS_EXCHANGER)
            .on_event(DocumentParsingBegan, document_parsing_began_handler)
            .on_event(
                DocumentParsingEnded,
                document_parsing_ended_handler,
            )
        )

    events_handlers = events_handlers_builder.build()

    commands_handlers = (
        CommandHandlersBuilder.from_channel(DOCUMENT_COMMANDS_CHANNEL)
        .on_message(DeleteDocument, delete_document_handler)
        .on_message(UnassignReviewer, unassign_reviewer_handler)
        .on_message(ImportDocument, import_document_handler)
        .on_message(SaveBatchDocuments, save_batch_documents_handler)
        .on_message(StartBatchProcessing, start_batch_processing_handler)
        .on_message(DeleteBatchDocument, delete_batch_document_handler)
        .and_from_channel(VALIDATION_COMMANDS_REPLIES_CHANNEL)
        .on_message(ValidationReply, validation_reply_handler)
        .and_from_channel(SERVICE_CHANNEL)
        .on_message(CreateDocument, create_document_handler)
        .on_message(CreateDocumentFromFile, create_document_from_file_handler)
        .on_message(UpdateDocumentState, update_state_handler)
        .on_message(AssignDocumentType, assign_document_type)
        .on_message(UpdateContainerData, update_document_container_data)
        .and_from_channel(DOCUMENT_COMMANDS_REPLIES_CHANNEL)
        .on_message(GetDocumentTypesReply, get_document_types_reply_handler)
        .on_message(GetGroupsReply, get_groups_reply_handler)
        .for_queue(COMMANDS_QUEUE)
        .build()
    )

    ded = DomainEventDispatcher(events_handlers, consumer)
    ded.initialize()

    cd = CommandDispatcher(commands_handlers, consumer, producer)
    cd.initialize()

    return consumer
