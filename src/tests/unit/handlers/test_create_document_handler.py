import random

from deps_documents.application.document.v2.protection_proxy import (
    DocumentAccessService,
)
from deps_documents.events_handler.command_handlers import create_document_handler


def test_create_document_handler__metadata_saved(create_document_command_message, mocker):
    document_id = str(random.randint(1, 100))
    mocker.patch.object(DocumentAccessService, "create_document", return_value=document_id)

    save_metadata = mocker.patch.object(DocumentAccessService, "save_metadata")
    create_document_handler(create_document_command_message)
    save_metadata.assert_called_with(document_id, create_document_command_message.command.document_metadata)


def test_create_document_handler__parent_id_saved(create_document_command_message, mocker):
    parent_id = str(random.randint(1, 100))
    create_document_command_message.command.parent_id = parent_id

    create_document = mocker.patch.object(DocumentAccessService, "create_document")
    create_document_handler(create_document_command_message)

    assert create_document.call_args[1]["parent_id"] == parent_id
