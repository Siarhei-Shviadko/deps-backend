import pytest

from deps_documents.domain.dtos import DocumentListFilterObject
from deps_documents.domain.exceptions import ForbiddenError
from deps_documents.infrastructure.access_management.context_vars import user


@pytest.fixture
def user_based_document_service_access_manager(document_service_access_manager):
    return document_service_access_manager.user()


@pytest.mark.usefixtures("set_test_user")
class TestUserBasedDocumentServiceAccessManager:
    def test_check_is_accessible_create__accessible__nothing_raises(self, user_based_document_service_access_manager):
        user_based_document_service_access_manager.check_is_accessible_create()

    def test_check_is_accessible_read__accessible__nothing_raises(
        self, user_based_document_service_access_manager, uow, document_fixture, user_fixture
    ):
        uow.document.add_document_to_user(document_fixture.pk, user_fixture["subject"])

        user_based_document_service_access_manager.check_is_accessible_read([document_fixture.pk])

    def test_check_is_accessible_read__not_accessible__forbidden_raises(
        self, user_based_document_service_access_manager, document_fixture, user_fixture
    ):
        with pytest.raises(ForbiddenError):
            user_based_document_service_access_manager.check_is_accessible_read([document_fixture.pk])

    def test_check_is_accessible_write__accessible__nothing_raises(
        self, user_based_document_service_access_manager, uow, document_fixture, user_fixture
    ):
        uow.document.add_document_to_user(document_fixture.pk, user_fixture["subject"])

        user_based_document_service_access_manager.check_is_accessible_write([document_fixture.pk])

    def test_check_is_accessible_write__not_accessible__forbidden_raises(
        self, user_based_document_service_access_manager, document_fixture, user_fixture
    ):
        with pytest.raises(ForbiddenError):
            user_based_document_service_access_manager.check_is_accessible_write([document_fixture.pk])

    def test_add_permissions_after_creating__permissions_added(
        self, user_based_document_service_access_manager, document_fixture, uow
    ):
        user_based_document_service_access_manager.add_permissions_after_creating(document_fixture.pk)

        assert document_fixture.pk in uow.document.get_user_document_entity_pks(user.get()["subject"])

    def test_patch_filter__filter_patched(self, user_based_document_service_access_manager, document_fixture):
        filter_obj = DocumentListFilterObject()
        user_based_document_service_access_manager.add_permissions_after_creating(document_fixture.pk)

        user_based_document_service_access_manager.patch_filter(filter_obj)

        assert filter_obj.ids == [document_fixture.pk]
