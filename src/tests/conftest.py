import pytest
from pytest_factoryboy import register
from starlette.testclient import TestClient

from deps_documents.app import create_app
from deps_documents.infrastructure.access_management.context_vars import user
from tests.factories.document_entity import DocumentMetadataFactory
from tests.fakes import FakeCommandProducer


@pytest.fixture(scope="session", autouse=True)
def app():
    fastapi_app = create_app()

    return fastapi_app


@pytest.fixture(scope="session", autouse=True)
def container(app):
    yield app.container


@pytest.fixture
def application(container):
    return container.application


@pytest.fixture(autouse=True)
def fake_command_producer(container):
    with container.command_producers.producer.override(FakeCommandProducer()) as cp:
        yield cp()
        del cp().last_sended


@pytest.fixture
def document_service_v3_mock(mocker, application):
    mock = mocker.Mock(application.document_v3.cls)
    application.document_v3.override(mock)
    yield mock

    application.document_v3.reset_override()


@pytest.fixture
def group_service_mock(mocker, application):
    mock = mocker.Mock(application.group.cls)
    application.group.override(mock)
    yield mock

    application.group.reset_override()


@pytest.fixture(scope="session", autouse=True)
def config(app):
    yield app.container.config


@pytest.fixture(scope="function")
def client(app):
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def repositories(app):
    yield app.container.repositories


@pytest.fixture(scope="function")
def units_of_work(app):
    yield app.container.units_of_work


@pytest.fixture(scope="function", autouse=True)
def use_cases(app):
    yield app.container.use_cases


@pytest.fixture(scope="function", autouse=True)
def app_services(app):
    yield app.container.application_services


@pytest.fixture(scope="function", autouse=True)
def domain_services(app):
    yield app.container.domain_services


@pytest.fixture(autouse=True)
def domain_services_accessor(app):
    yield app.container.domain_services_accessor


@pytest.fixture
def enable_authorization_for_container(config):
    config.authentication.enabled.override(True)
    yield
    config.authentication.enabled.override(False)


@pytest.fixture
def enable_reviewer_reassign(config):
    config.reviewer_reassign_enabled.override(True)
    yield
    config.reviewer_reassign_enabled.override(False)


@pytest.fixture
def enable_authorization_for_services(app):
    app.container.services.config.authentication.enabled.override(True)
    yield
    app.container.services.config.authentication.enabled.override(False)


@pytest.fixture(autouse=True)
def document_service_access_manager(app):
    yield app.container.document_service_access_manager


@pytest.fixture(scope="function")
def datasources(app):
    yield app.container.datasources


@pytest.fixture
def tenant_id():
    return "deps-users"


@pytest.fixture
def user_fixture(tenant_id):
    return {
        "subject": "some_user_id",
        "roles": [],
        "groups": ["deps-users"],
        "token": "token",
        "email": "example@mail.com",
        "first_name": "John",
        "last_name": "Doe",
        "organisation": tenant_id,
    }


@pytest.fixture
def set_test_user(user_fixture):
    user.set(user_fixture)
    yield
    user.set(None)


@pytest.fixture
def admin_fixture():
    return {
        "subject": "some_admin_id",
        "roles": [],
        "groups": ["deps-admins"],
        "token": "token",
        "email": "example@mail.com",
        "first_name": "John",
        "last_name": "Doe",
        "organisation": "deps-admins",
    }


@pytest.fixture
def set_admin_user(admin_fixture):
    user.set(admin_fixture)
    yield
    user.set(None)


@pytest.fixture(params=[[], ["deps-users", "deps-admins"]])
def forbidden_user_fixture(request):
    return {
        "subject": "some_user_id",
        "roles": [],
        "groups": request.param,
        "token": "token",
        "email": "example@mail.com",
        "first_name": "John",
        "last_name": "Doe",
        "organisation": "test_org",
    }


@pytest.fixture
def set_forbidden_user(forbidden_user_fixture):
    user.set(forbidden_user_fixture)
    yield
    user.set(None)


@pytest.fixture(autouse=True)
def label_service_access_manager(app):
    yield app.container.label_service_access_manager


@pytest.fixture(scope="function")
def uow(units_of_work):
    yield units_of_work.uow


register(DocumentMetadataFactory)
