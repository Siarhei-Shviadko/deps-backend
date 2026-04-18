import pytest

from tests.factories import DocumentEntityFactory, LabelEntityFactory

TEST_DOCUMENT_PK = "1"
TEST_LABEL_PK = "1"


@pytest.fixture
def enable_group_based_access_management(config):
    config.authentication.document_permission_rule.override("group")
    yield
    config.authentication.document_permission_rule.override("none")


@pytest.fixture
def document_service_mock(mocker, domain_services):
    mock = mocker.Mock(domain_services.document.cls)
    domain_services.document.override(mock)
    yield mock

    domain_services.document.reset_override()


@pytest.fixture
def document_fixture(uow):
    return uow.document.add(DocumentEntityFactory(pk=TEST_DOCUMENT_PK))


@pytest.fixture
def label_fixture(uow):
    return uow.label.add(LabelEntityFactory(pk=TEST_LABEL_PK))
