from contextlib import ExitStack
from random import randint
from uuid import uuid4

import pytest
from dependency_injector.providers import (
    DependenciesContainer,
    Dependency,
    Selector,
    Self,
)
from deps_message_flow.commands.consumer import CommandMessage
from sqlalchemy.engine.base import Connection

from deps_documents.events_handler.command_handlers import CreateDocumentFromFile
from deps_documents.infrastructure.access_management.document_access_manager import (
    DocumentServiceAccessManagerTrap,
)
from deps_documents.infrastructure.access_management.label_access_manager import (
    LabelServiceAccessManagerTrap,
)
from tests.factories import BlobFileFactory, DocumentEntityFactory
from tests.fakes import FakeObjectStorageProxy

DO_NOT_OVERRIDE_OBJS = (Self, DependenciesContainer, Dependency)


def mock_container_provider(container, mocker):
    with ExitStack() as context:
        for provider in filter(lambda x: not isinstance(x, DO_NOT_OVERRIDE_OBJS), container):
            context.enter_context(provider.override(mocker.Mock(provider.cls)))

        yield container


@pytest.fixture(scope="function", autouse=True)
def services(mocker, app):
    with ExitStack() as context:
        for service_provider in filter(
            lambda x: not isinstance(x, DO_NOT_OVERRIDE_OBJS), app.container.services.providers.values()
        ):
            if isinstance(service_provider, Selector):
                first_selector_provider = next(iter(service_provider.providers.values()))
                context.enter_context(service_provider.override(mocker.Mock(first_selector_provider.cls)))
                continue

            context.enter_context(service_provider.override(mocker.Mock(service_provider.cls)))

        yield app.container.services

    app.container.services.reset_override()


@pytest.fixture(scope="function", autouse=True)
def repositories(repositories, mocker):
    with ExitStack() as context:
        for repository in filter(lambda x: not isinstance(x, DO_NOT_OVERRIDE_OBJS), repositories.providers.values()):
            context.enter_context(repository.override(mocker.MagicMock(repository.cls)))

        yield repositories

    repositories.reset_override()


@pytest.fixture(scope="function")
def database(app, mocker):
    database = app.container.datasources.postgres_datasource()
    original_method = database.get_connection
    database.get_connection = mocker.Mock(Connection)

    yield database

    database.get_connection = original_method


@pytest.fixture(scope="function")
def database_connection(database):
    yield database.get_connection()


@pytest.fixture(scope="function")
def responses():
    import responses

    with responses.RequestsMock() as rsps:
        yield rsps


def _mock_file_url_service(service, mocker, faker):
    mock = mocker.Mock(service)
    mock.get_external.return_value = faker.image_url()
    mock.get_internal.return_value = faker.image_url()
    return mock


@pytest.fixture(scope="function")
def use_cases_mock(use_cases, mocker):
    with ExitStack() as context:
        for use_case in filter(lambda x: not isinstance(x, DO_NOT_OVERRIDE_OBJS), use_cases.providers.values()):
            context.enter_context(use_case.override(mocker.Mock(use_case.cls)))

        yield use_cases

    use_cases.reset_override()


@pytest.fixture(autouse=True)
def application_services(app_services, mocker, faker):
    with ExitStack() as context:
        context.enter_context(app_services.file_url.override(_mock_file_url_service(app_services.file_url.cls, mocker, faker)))

        yield app_services

    app_services.reset_override()


@pytest.fixture
def document_service_mock(mocker, domain_services):
    mock = mocker.Mock(domain_services.document.cls)
    domain_services.document.override(mock)

    return mock


@pytest.fixture
def label_service_mock(mocker, domain_services):
    mock = mocker.Mock(domain_services.label.cls)
    domain_services.label.override(mock)

    return mock


@pytest.fixture
def no_restrictions_document_access_manager():
    yield DocumentServiceAccessManagerTrap


@pytest.fixture
def document_access_manager_mock(mocker, no_restrictions_document_access_manager, document_service_access_manager):
    mock = mocker.Mock(no_restrictions_document_access_manager)
    document_service_access_manager.override(mock)

    return mock


@pytest.fixture
def no_restrictions_label_access_manager():
    yield LabelServiceAccessManagerTrap


@pytest.fixture
def label_access_manager_mock(mocker, no_restrictions_label_access_manager, label_service_access_manager):
    mock = mocker.Mock(no_restrictions_label_access_manager)
    label_service_access_manager.override(mock)

    return mock


@pytest.fixture
def document_file_service_mock(mocker, domain_services):
    mock = mocker.Mock(domain_services.document_file.cls)
    domain_services.document_file.override(mock)
    return mock


@pytest.fixture
def blob_storage_mock(container):
    with container.services.object_storage.override(FakeObjectStorageProxy()) as fsp:
        yield fsp()


@pytest.fixture
def document_entity_with_processing_documents():
    entity = DocumentEntityFactory()
    entity.processing_documents = [BlobFileFactory() for _ in range(randint(1, 3))]
    return entity


@pytest.fixture
def priority_managers(app, mocker):
    with ExitStack() as context:
        for priority_manager in filter(
            lambda x: not isinstance(x, DO_NOT_OVERRIDE_OBJS), app.container.priority_managers.providers.values()
        ):
            context.enter_context(priority_manager.override(mocker.MagicMock(priority_manager.cls)))

        yield app.container.priority_managers

    app.container.priority_managers.reset_override()


@pytest.fixture
def postgres_datasource_mock(mocker, datasources):
    mock = mocker.Mock(datasources.postgres_datasource())
    datasources.postgres_datasource.override(mock)

    yield mock

    datasources.reset_override()


@pytest.fixture
def valid_decoded_token():
    return {"groups": ["Test group"]}


@pytest.fixture(params=[[], ["Test group 1", "Test group 2"]])
def invalid_decoded_token(request):
    return {"groups": request.param}


@pytest.fixture
def uow(units_of_work, repositories, mocker):
    uow_mock = mocker.MagicMock(units_of_work.uow.cls)
    # already overriden
    uow_mock.document = repositories.document()
    uow_mock.comment = repositories.comment()
    uow_mock.document_log = repositories.document_log()
    uow_mock.analytics = repositories.analytics()
    uow_mock.label = repositories.label()
    uow_mock.relation = repositories.relation()
    uow_mock.group = repositories.group()

    uow_mock.__enter__ = lambda self: self

    units_of_work.uow.override(uow_mock)
    yield units_of_work.uow()
    units_of_work.uow.reset_override()


@pytest.fixture
def create_document_command_message(mocker):
    cm = mocker.Mock(CommandMessage)
    cm.command.document_name = uuid4().hex
    cm.command.document_type_id = uuid4().hex
    cm.command.engine = "TESSERACT"
    cm.command.language = "eng"
    cm.command.files = [uuid4().hex]
    cm.command.assign_to_me = False
    cm.command.document_metadata = {"extension": "jpeg"}
    cm.command.parent_id = None
    return cm


@pytest.fixture
def create_document_from_file_command_message(mocker):
    cm = mocker.Mock(CommandMessage)
    cm.command = CreateDocumentFromFile(
        document_name=uuid4().hex,
        file_path=f"blobs/{uuid4().hex}.pdf",
        document_type_id=uuid4().hex,
    )

    return cm
