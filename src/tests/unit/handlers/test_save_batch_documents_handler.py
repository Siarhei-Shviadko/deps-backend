import json

from deps_documents.application import DocumentAccessServiceV3
from deps_documents.events_handler.command_handlers import save_batch_documents_handler


def test_save_batch_documents__saved(save_batch_documents_command, document_id, mocker):
    mocker.patch.object(DocumentAccessServiceV3, "create_document_with_existing_file", return_value=document_id)
    response = save_batch_documents_handler(command_message=save_batch_documents_command, tenant_id="tenant_id")
    mocker.resetall()
    assert response
    response_payload = json.loads(response[0].payload)
    assert response_payload == {
        "batch_id": save_batch_documents_command.command.batch_id,
        "files": [
            {"id": file["id"], "document_id": document_id, "error": None} for file in save_batch_documents_command.command.files
        ],
    }


def test_save_batch_documents__failed(save_batch_documents_command, mocker):
    mocker.patch.object(DocumentAccessServiceV3, "create_document_with_existing_file", side_effect=ZeroDivisionError())
    response = save_batch_documents_handler(command_message=save_batch_documents_command, tenant_id="tenant")
    mocker.resetall()
    assert response
    response_payload = json.loads(response[0].payload)
    assert response_payload == {
        "batch_id": save_batch_documents_command.command.batch_id,
        "files": [
            {"id": file["id"], "document_id": None, "error": {"code": "no code", "message": "ZeroDivisionError()"}}
            for file in save_batch_documents_command.command.files
        ],
    }
