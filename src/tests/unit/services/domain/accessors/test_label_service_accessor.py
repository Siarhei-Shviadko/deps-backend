import pytest

from deps_documents.domain.dtos import LabelListFilterObject
from tests.factories.document_entity import LabelEntityFactory


@pytest.mark.usefixtures("enable_authorization_for_container", "set_test_user")
class TestLabelServiceAccessor:
    label_pk = "1"
    label_entity = LabelEntityFactory(pk=label_pk)

    def test_create__access_granted(self, label_service_mock, label_access_manager_mock, domain_services_accessor):
        label_service_mock.create.return_value = self.label_entity
        result = domain_services_accessor.label().create(self.label_entity)

        assert result == self.label_entity
        label_access_manager_mock.check_uniqueness.assert_called_with(self.label_entity.name)
        label_access_manager_mock.add_permissions_after_creating.assert_called_with(self.label_pk)

    def test_get_list__is_access__success(self, label_service_mock, label_access_manager_mock, domain_services_accessor):
        label_list = [LabelEntityFactory()]

        label_service_mock.get_list.return_value = label_list
        filter_object = LabelListFilterObject()
        result = domain_services_accessor.label().get_list(filter_object)

        assert result == label_list
        label_access_manager_mock.patch_filter.assert_called_with(filter_object)
