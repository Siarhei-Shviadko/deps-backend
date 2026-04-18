import pytest


@pytest.fixture
def document_file_service_mock(mocker, domain_services):
    mock = mocker.Mock(domain_services.document_file.cls)
    domain_services.document_file.override(mock)

    return mock
