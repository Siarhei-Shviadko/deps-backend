import pytest

from deps_documents.constants import (
    DOCUMENT_COMMANDS_REPLIES_CHANNEL,
    WORKFLOW_MANAGER_COMMANDS_CHANNEL,
)
from deps_documents.domain.model import ProcessDocument
from deps_documents.events_handler.command_handlers import (
    start_batch_processing_handler,
)


@pytest.mark.usefixtures("set_test_user", "fake_uow")
@pytest.mark.batch
def test_handler__ok(fake_command_producer, start_batch_processing_command, document, tenant_id):
    start_batch_processing_handler(start_batch_processing_command)

    sent_message = fake_command_producer.last_sended
    assert sent_message.channel == WORKFLOW_MANAGER_COMMANDS_CHANNEL
    assert sent_message.reply_to == DOCUMENT_COMMANDS_REPLIES_CHANNEL
    assert sent_message.command == ProcessDocument(
        document_id=document.pk,
        tenant_id=tenant_id,
        files=[f.blob_name for f in document.files],
        document_type_id=document.document_type,
        engine=document.engine,
        language=document.language,
        llm_type=document.llm_type,
        parsing_features=document.parsing_features and sorted(document.parsing_features),
        needs_unification=document.needs_unification,
        needs_extraction=document.needs_extraction,
        needs_parsing=document.needs_parsing,
    )
