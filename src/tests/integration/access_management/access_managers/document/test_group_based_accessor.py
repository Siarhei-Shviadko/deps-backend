import pytest

from deps_documents.domain.dtos import DocumentListFilterObject
from deps_documents.domain.exceptions import ForbiddenError
from tests.factories import DocumentEntityFactory


@pytest.fixture
def group_based_document_service_access_manager(document_service_access_manager):
    return document_service_access_manager.group()


@pytest.mark.usefixtures("set_test_user")
class TestGroupBasedDocumentServiceAccessManagerForUser:
    def test_check_is_accessible_create__accessible__nothing_raises(self, group_based_document_service_access_manager):
        group_based_document_service_access_manager.check_is_accessible_create()

    def test_check_is_accessible_read__accessible__nothing_raises(
        self, group_based_document_service_access_manager, uow, document_fixture, user_fixture
    ):
        uow.document.add_document_to_user(document_fixture.pk, user_fixture["subject"])
        group_based_document_service_access_manager.check_is_accessible_read([document_fixture.pk])

    def test_check_is_accessible_read__not_accessible__forbidden_raises(
        self, group_based_document_service_access_manager, document_fixture
    ):
        with pytest.raises(ForbiddenError):
            group_based_document_service_access_manager.check_is_accessible_read([document_fixture.pk])

    def test_check_is_accessible_write__accessible__nothing_raises(
        self, group_based_document_service_access_manager, uow, document_fixture, user_fixture
    ):
        uow.document.add_document_to_user(document_fixture.pk, user_fixture["subject"])
        group_based_document_service_access_manager.check_is_accessible_write([document_fixture.pk])

    def test_check_is_accessible_write__not_accessible__forbidden_raises(
        self, group_based_document_service_access_manager, document_fixture
    ):
        with pytest.raises(ForbiddenError):
            group_based_document_service_access_manager.check_is_accessible_write([document_fixture.pk])

    def test_add_permissions_after_creating__permissions_added(
        self, group_based_document_service_access_manager, uow, document_fixture, user_fixture
    ):
        group_based_document_service_access_manager.add_permissions_after_creating(document_fixture.pk)
        assert document_fixture.pk in uow.document.get_user_document_entity_pks(user_fixture["subject"])

    def test_patch_filter__user_has_documents__filter_patched(
        self, group_based_document_service_access_manager, document_fixture
    ):
        filter_obj = DocumentListFilterObject()
        group_based_document_service_access_manager.add_permissions_after_creating(document_fixture.pk)
        group_based_document_service_access_manager.patch_filter(filter_obj)

        assert filter_obj.ids == [document_fixture.pk]

    def test_patch_filter__user_has_no_documents__filter_patched(self, group_based_document_service_access_manager):
        filter_obj = DocumentListFilterObject()
        group_based_document_service_access_manager.patch_filter(filter_obj)

        assert filter_obj.ids == []


@pytest.mark.usefixtures("set_admin_user")
class TestGroupBasedDocumentServiceAccessManagerForAdmin:
    def test_check_is_accessible_create__accessible__nothing_raises(self, group_based_document_service_access_manager):
        group_based_document_service_access_manager.check_is_accessible_create()

    def test_check_is_accessible_read__accessible__nothing_raises(
        self, group_based_document_service_access_manager, document_fixture
    ):
        group_based_document_service_access_manager.check_is_accessible_read([document_fixture.pk])

    def test_check_is_accessible_write__accessible__nothing_raises(
        self, group_based_document_service_access_manager, document_fixture
    ):
        group_based_document_service_access_manager.check_is_accessible_write([document_fixture.pk])

    def test_add_permissions_after_creating__permissions_added(
        self, group_based_document_service_access_manager, uow, document_fixture, admin_fixture
    ):
        group_based_document_service_access_manager.add_permissions_after_creating(document_fixture.pk)
        assert document_fixture.pk in uow.document.get_user_document_entity_pks(admin_fixture["subject"])

    def test_patch_filter__filter_not_patched(self, group_based_document_service_access_manager, document_fixture):
        filter_obj = DocumentListFilterObject()
        group_based_document_service_access_manager.add_permissions_after_creating(document_fixture.pk)
        group_based_document_service_access_manager.patch_filter(filter_obj)

        assert filter_obj.ids is None
