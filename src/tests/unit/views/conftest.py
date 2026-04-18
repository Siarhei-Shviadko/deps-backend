import pytest


@pytest.fixture
def label_service_mock(mocker, domain_services):
    mock = mocker.Mock(domain_services.label.cls)
    domain_services.label.override(mock)

    return mock


@pytest.fixture
def document_log_service_mock(mocker, domain_services):
    mock = mocker.Mock(domain_services.document_log.cls)
    domain_services.document_log.override(mock)

    return mock
