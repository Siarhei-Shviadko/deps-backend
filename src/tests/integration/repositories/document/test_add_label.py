import pytest

from deps_documents.domain.entities import LabelEntity
from deps_documents.domain.exceptions import LabelNotFoundError, PrimaryKeyError
from tests.factories import DocumentEntityFactory


class TestCaseDocumentAddLabel:
    @classmethod
    def setup_class(cls):
        cls.label = LabelEntity(name="Test label")

    def test_add_label__existing_doc__return_updated_doc_pk(self, uow):
        document = uow.document.add(DocumentEntityFactory(labels=None))
        label = uow.label.add(self.label)

        response = uow.document.add_label(label.pk, [document.pk])

        assert len(response) == 1

    def test_add_label__existing_doc__add_label(self, uow):
        document = uow.document.add(DocumentEntityFactory(labels=None))
        label = uow.label.add(self.label)

        uow.document.add_label(label.pk, [document.pk])

        updated_document = uow.document.get(document.pk)

        assert len(updated_document.labels) == 1

    def test_add_label__not_existing_doc__return_empty_update_doc_pk(self, uow):
        label = uow.label.add(self.label)
        response = uow.document.add_label(label.pk, ["1"])

        assert len(response) == 0

    def test_add_label__not_valid_doc_return_pk_error(self, uow):
        label = uow.label.add(self.label)
        with pytest.raises(PrimaryKeyError):
            uow.document.add_label(label.pk, ["ad"])

    def test_remove_label__not_existing_label__raise_label_not_found(self, uow):
        document = uow.document.add(DocumentEntityFactory(labels=None))
        with pytest.raises(LabelNotFoundError):
            uow.document.add_label(self.label.pk, document.pk)
