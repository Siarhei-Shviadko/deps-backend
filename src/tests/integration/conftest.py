import uuid

import pytest
from dependency_injector.providers import DependenciesContainer, Dependency, Self
from deps_object_storage import ObjectStorage

from deps_documents.domain.services import DocumentFileService

DO_NOT_OVERRIDE_OBJS = (Self, DependenciesContainer, Dependency)


@pytest.fixture(scope="session")
def database(app):
    database = app.container.datasources.postgres_datasource()
    yield database


@pytest.fixture(scope="function", autouse=True)
def session(app, database):
    connection = database.get_connection()

    class TrapForThreadLocalConnections:
        """
        This class is used instead of threading.local in Database, for allowing connection transactions management
        """

        connection = None

    TrapForThreadLocalConnections.connection = connection
    connection.begin()
    transaction = connection.begin_nested()
    database._registry = TrapForThreadLocalConnections
    try:
        yield
    finally:
        transaction.rollback()
    database.close()


@pytest.fixture(scope="function")
def blob_service(mocker):
    """Provides every blob unit test with clear media root."""
    blob_service_mock = mocker.Mock(ObjectStorage)
    blob_service_mock.upload.return_value = uuid.uuid4().hex

    yield blob_service_mock


@pytest.fixture(scope="function", autouse=True)
def services(app, blob_service):
    with app.container.services.object_storage.override(blob_service):
        yield app.container.services

    app.container.services.object_storage.reset_override()


@pytest.fixture(scope="function", autouse=True)
def label_entity_repository(units_of_work):
    with units_of_work.uow() as _uow:
        yield _uow.label


@pytest.fixture(scope="function")
def uow(units_of_work):
    with units_of_work.uow() as uow:
        yield uow


@pytest.fixture(scope="function", autouse=True)
def document_file_service(mocker, domain_services):
    document_file_service_mock = mocker.Mock(DocumentFileService)
    document_file_service_mock.retrieve_file_content.return_value = b"Test file"

    with domain_services.document_file.override(document_file_service_mock):
        yield document_file_service_mock
    domain_services.document_file.reset_override()
