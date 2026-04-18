import pytest

from deps_documents.domain.exceptions import ForbiddenError
from deps_documents.infrastructure.access_management.context_vars import user


@pytest.fixture
def role_based_document_service_accessor(document_service_access_manager):
    return document_service_access_manager.role()


class TestRoleBasedDocumentServiceAccessor:
    def test_check_is_accessible_create__user_has_create_role__nothing_raises(self, role_based_document_service_accessor, config):
        user_dict = {
            "subject": "some_user_id",
            "roles": [config.authentication.create_role()],
            "groups": [],
            "token": "token",
            "email": "example@mail.com",
            "first_name": "John",
            "last_name": "Doe",
        }
        user.set(user_dict)

        role_based_document_service_accessor.check_is_accessible_create()
        user.set(None)

    def test_check_is_accessible_create__user_has_not_create_role__forbidden_raises(self, role_based_document_service_accessor):
        user_dict = {
            "subject": "some_user_id",
            "roles": ["some_wrong_role"],
            "groups": [],
            "token": "token",
            "email": "example@mail.com",
            "first_name": "John",
            "last_name": "Doe",
        }
        user.set(user_dict)

        with pytest.raises(ForbiddenError):
            role_based_document_service_accessor.check_is_accessible_create()

        user.set(None)

    def test_check_is_accessible_read__user_has_read_role__nothing_raises(self, role_based_document_service_accessor, config):
        user_dict = {
            "subject": "some_user_id",
            "roles": [config.authentication.read_role()],
            "groups": [],
            "token": "token",
            "email": "example@mail.com",
            "first_name": "John",
            "last_name": "Doe",
        }
        user.set(user_dict)

        role_based_document_service_accessor.check_is_accessible_read(["doc_id"])

        user.set(None)

    def test_check_is_accessible_read__user_has_not_read_role__forbidden_raises(self, role_based_document_service_accessor):
        user_dict = {
            "subject": "some_user_id",
            "roles": ["some_wrong_role"],
            "groups": [],
            "token": "token",
            "email": "example@mail.com",
            "first_name": "John",
            "last_name": "Doe",
        }
        user.set(user_dict)

        with pytest.raises(ForbiddenError):
            role_based_document_service_accessor.check_is_accessible_read(["doc_id"])

        user.set(None)

    def test_check_is_accessible_write__user_has_write_role__nothing_raises(self, role_based_document_service_accessor, config):
        user_dict = {
            "subject": "some_user_id",
            "roles": [config.authentication.write_role()],
            "groups": [],
            "token": "token",
            "email": "example@mail.com",
            "first_name": "John",
            "last_name": "Doe",
        }
        user.set(user_dict)

        role_based_document_service_accessor.check_is_accessible_write(["doc_id"])

        user.set(None)

    def test_check_is_accessible_write__user_has_not_write_role__forbidden_raises(self, role_based_document_service_accessor):
        user_dict = {
            "subject": "some_user_id",
            "roles": ["some_wrong_role"],
            "groups": [],
            "token": "token",
            "email": "example@mail.com",
            "first_name": "John",
            "last_name": "Doe",
        }
        user.set(user_dict)

        with pytest.raises(ForbiddenError):
            role_based_document_service_accessor.check_is_accessible_write(["doc_id"])

        user.set(None)

    def test_add_permissions_after_creating__nothing_raises(self, role_based_document_service_accessor):
        role_based_document_service_accessor.add_permissions_after_creating(["doc_id"])

    def test_patch_filter__nothing_raises(self, role_based_document_service_accessor):
        role_based_document_service_accessor.patch_filter("filter")
