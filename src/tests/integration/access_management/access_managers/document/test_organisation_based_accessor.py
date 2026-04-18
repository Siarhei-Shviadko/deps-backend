import pytest

from deps_documents.domain.exceptions import DocumentNotFoundError
from tests.factories import DocumentEntityFactory


@pytest.fixture
def org_access_manager(document_service_access_manager):
    return document_service_access_manager.organisation()


@pytest.fixture
def add_document_to_user_and_organisation(uow, document_fixture, user_fixture):
    uow.document.add_document_to_user_and_organisation(document_fixture.pk, user_fixture["subject"], user_fixture["groups"][0])
    return [document_fixture.pk]


class TestOrganisationBasedDocumentServiceAccessManagerForUser:
    def test__check_permission__positive(self, org_access_manager, set_test_user, add_document_to_user_and_organisation):
        org_access_manager._check_permission(add_document_to_user_and_organisation)

    def test__check_permission__no_permission(self, org_access_manager, set_test_user, document_fixture):
        with pytest.raises(DocumentNotFoundError) as excinfo:
            org_access_manager._check_permission(document_fixture.pk)

        assert f"Document `{document_fixture.pk}` not found." == str(excinfo.value)
