import pytest

from deps_documents.events_handler.command_handlers import delete_batch_document_handler
from tests.fakes import FakeDocumentRepository


@pytest.mark.usefixtures("set_test_user")
def test_delete_ok(delete_batch_document_command, uow, document):
    uow.document = FakeDocumentRepository({document.pk: document})

    delete_batch_document_handler(delete_batch_document_command)

    assert not uow.document.db
