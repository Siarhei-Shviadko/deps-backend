import pytest

from deps_documents.domain.entities import LabelEntity
from deps_documents.domain.exceptions import (
    DocumentNotFoundError,
    LabelForDocumentNotFoundError,
    LabelNotFoundError,
)
from tests.factories import DocumentEntityFactory


class TestCaseDocumentRemoveLabel:
    label = LabelEntity(name="Test label")

    def test_remove_label__existing_doc__return_true(self, uow):
        document = uow.document.add(DocumentEntityFactory(labels=None))
        label = uow.label.add(self.label)
        uow.document.add_label(label.pk, [document.pk])

        response = uow.document.remove_label(label.pk, document.pk)

        assert response

    def test_remove_label__existing_doc__remove_label(self, uow):
        document = uow.document.add(DocumentEntityFactory(labels=None))
        label = uow.label.add(self.label)
        uow.document.add_label(label.pk, [document.pk])

        uow.document.remove_label(label.pk, document.pk)

        updated_document = uow.document.get(document.pk)

        assert not updated_document.labels

    def test_remove_label__not_existing_doc__raise_document_not_found(self, uow):
        label = uow.label.add(self.label)
        with pytest.raises(DocumentNotFoundError):
            uow.document.remove_label(label.pk, "1")

    def test_remove_label__not_existing_label__raise_label_not_found(self, uow):
        document = uow.document.add(DocumentEntityFactory(labels=None))
        with pytest.raises(LabelNotFoundError):
            uow.document.remove_label("1", document.pk)

    def test_remove_label__not_document_label__raise_label_for_doc_not_found(self, uow):
        document = uow.document.add(DocumentEntityFactory(labels=None))
        label = uow.label.add(self.label)
        with pytest.raises(LabelForDocumentNotFoundError):
            uow.document.remove_label(label.pk, document.pk)
