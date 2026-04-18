import pytest

from deps_documents.domain.dtos import LabelListFilterObject
from tests.factories.document_entity import LabelEntityFactory


class TestCaseOrganisationLabels:
    def test_add_label_to_organisation__label_added(self, label_entity_repository):
        label = label_entity_repository.add(LabelEntityFactory())
        organisation_name = "Test organisation"

        label_entity_repository.add_label_to_organisation(label.pk, organisation_name)

        organisation_label_pks = label_entity_repository.get_organisation_label_entity_pks(
            organisation_name, LabelListFilterObject()
        )

        assert organisation_label_pks == [label.pk]

    def test_get_organisation_label_entity_pks__labels_filtered_by_organisation(self, label_entity_repository):
        label = label_entity_repository.add(LabelEntityFactory())
        first_organisation_name = "Test organisation 1"
        second_organisation_name = "Test organisation 2"

        label_entity_repository.add_label_to_organisation(label.pk, first_organisation_name)

        organisation_label_pks = label_entity_repository.get_organisation_label_entity_pks(
            second_organisation_name, LabelListFilterObject()
        )

        assert len(organisation_label_pks) == 0

    def test_get_organisation_label_entity_pks__labels_filtered_by_organisation_and_name(self, label_entity_repository):
        first_label = label_entity_repository.add(LabelEntityFactory(name="Test_1"))
        second_label = label_entity_repository.add(LabelEntityFactory(name="Test_2"))
        third_label = label_entity_repository.add(LabelEntityFactory(name="Test_1"))

        first_organisation_name = "Test organisation 1"
        second_organisation_name = "Test organisation 2"

        label_entity_repository.add_label_to_organisation(first_label.pk, first_organisation_name)
        label_entity_repository.add_label_to_organisation(second_label.pk, first_organisation_name)
        label_entity_repository.add_label_to_organisation(third_label.pk, second_organisation_name)

        organisation_label_pks = label_entity_repository.get_organisation_label_entity_pks(
            first_organisation_name, LabelListFilterObject(name="Test_1")
        )

        assert organisation_label_pks == [first_label.pk]
