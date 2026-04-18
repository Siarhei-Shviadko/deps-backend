from uuid import uuid4

import pytest

from deps_documents.domain.entities import DocumentTypeEntity
from tests.fakes import FakeDocumentTypeRepository, FakeGroupRepository


@pytest.fixture
def application(container):
    return container.application


@pytest.fixture
def document_service_mock(mocker, application):
    mock = mocker.Mock(application.document.cls)
    application.document.override(mock)
    yield mock

    application.document.reset_override()


@pytest.fixture
def document_type_service(uow, application):
    uow.document_type = FakeDocumentTypeRepository()

    return application.document_type()


@pytest.fixture
def group_service(uow, application):
    uow.group = FakeGroupRepository()

    return application.group()


@pytest.fixture
def test_document_type():
    return DocumentTypeEntity(
        id=str(uuid4()),
        tenant=str(uuid4()),
        name=str(uuid4()),
    )
