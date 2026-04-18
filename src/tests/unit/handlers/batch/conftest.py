from random import randint

import pytest
from deps_message_flow.commands.consumer import CommandMessage

from deps_documents.domain.entities import DocumentEntity, DocumentEntityPk
from deps_documents.events_handler.command_handlers import (
    DeleteBatchDocument,
    StartBatchProcessing,
)
from deps_documents.infrastructure.document_uow import DocumentUnitOfWork
from tests.factories import DocumentEntityFactory
from tests.fakes import FakeDocumentRepository


@pytest.fixture
def document_pk() -> DocumentEntityPk:
    return DocumentEntityPk(str(randint(10, 100)))


@pytest.fixture
def document(document_pk) -> DocumentEntity:
    return DocumentEntityFactory(pk=document_pk)


@pytest.fixture
def fake_uow(uow, document) -> DocumentUnitOfWork:
    uow.document = FakeDocumentRepository({int(document.pk): document})

    return uow


@pytest.fixture
def start_batch_processing_command(mocker, document_pk) -> CommandMessage[StartBatchProcessing]:
    cm = mocker.Mock(CommandMessage)
    cm.command = StartBatchProcessing([document_pk])

    return cm


@pytest.fixture()
def delete_batch_document_command(mocker, document_pk) -> CommandMessage[DeleteBatchDocument]:
    cm = mocker.Mock(CommandMessage)
    cm.command = DeleteBatchDocument(document_pk)

    return cm
