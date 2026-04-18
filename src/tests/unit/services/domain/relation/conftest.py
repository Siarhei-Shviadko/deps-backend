import pytest


@pytest.fixture
def relation_service_mock(mocker, domain_services):
    mock = mocker.Mock(domain_services.relation.cls)
    domain_services.relation.override(mock)
    return mock


@pytest.fixture
def relation_service(domain_services):
    domain_services.relation.reset_override()
    return domain_services.relation()
