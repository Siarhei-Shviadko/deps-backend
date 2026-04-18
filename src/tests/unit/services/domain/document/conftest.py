import pytest


@pytest.fixture
def domain_services(domain_services):
    domain_services.document.reset_override()

    return domain_services
