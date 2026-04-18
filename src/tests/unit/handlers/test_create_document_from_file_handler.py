from uuid import uuid4

import pytest

from deps_documents.application.document.v3.protection_proxy import (
    DocumentAccessService as DocumentAccessServiceV3,
)
from deps_documents.events_handler.command_handlers import (
    create_document_from_file_handler,
)


@pytest.mark.usefixtures("set_test_user")
def test_create_document_from_file_handler__basic_parameters__document_created(
    create_document_from_file_command_message,
    mocker,
):
    document_id = str(uuid4())
    create_document_mock = mocker.patch.object(
        DocumentAccessServiceV3,
        "create_document_with_existing_file",
        return_value=document_id,
    )

    result = create_document_from_file_handler(create_document_from_file_command_message)

    assert len(result) == 1
    create_document_mock.assert_called_once()
    call_kwargs = create_document_mock.call_args[1]
    assert call_kwargs["document_name"] == create_document_from_file_command_message.command.document_name
    assert call_kwargs["group_id"] == create_document_from_file_command_message.command.group_id
    assert call_kwargs["blob_name"] == create_document_from_file_command_message.command.file_path
    assert call_kwargs["document_type_id"] == create_document_from_file_command_message.command.document_type_id
