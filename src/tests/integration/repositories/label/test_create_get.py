from deps_documents.domain.dtos import LabelListFilterObject
from deps_documents.domain.entities.label import LabelEntity


class TestCaseLabelRepository:
    @classmethod
    def setup_class(cls):
        cls.label = LabelEntity("Test label")

    def test_create__valid_label__return_label(self, uow):
        label = uow.label.add(self.label)

        assert label.name

    def test_get_list__not_empty__return_label_list(self, uow):
        uow.label.add(self.label)
        result = uow.label.get_list(LabelListFilterObject())

        assert len(result) == 1

    def test_get_list__empty__return_empty_list(self, uow):
        result = uow.label.get_list(LabelListFilterObject())

        assert len(result) == 0
