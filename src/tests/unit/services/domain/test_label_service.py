import pytest

from deps_documents.domain.dtos import LabelListFilterObject
from deps_documents.domain.entities import LabelEntity


@pytest.fixture
def domain_services(domain_services):
    domain_services.label.reset_override()

    return domain_services


class TestLabelService:
    def test_create__many_data__return_label_entity(self, domain_services, uow):
        label_name = "Label name"
        uow.label.add.return_value = LabelEntity(label_name)

        label_entity = domain_services.label().create(LabelEntity(label_name))

        assert label_entity.name == label_name

    def test_get_list__many_data__return_label_entity_list(self, domain_services, uow):
        label_name = "Label name"
        uow.label.get_list.return_value = [LabelEntity(label_name)]

        labels = domain_services.label().get_list(LabelListFilterObject())

        assert len(labels) == 1
