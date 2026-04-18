import pytest

from deps_documents.domain.entities.document_pk import DocumentEntityPk
from deps_documents.domain.exceptions import PrimaryKeyError
from tests.factories.document_entity import DocumentEntityFactory


class TestCaseDocumentBatchDeleteUseCase:
    def test_execute__valid_data__return_success(self, domain_services, uow):
        doc = DocumentEntityFactory(pk="1")
        uow.document.get.return_value = doc
        uow.document.get_descendants.return_value = []

        result = domain_services.document().batch_delete([doc.pk])
        expected_response = [DocumentEntityPk(doc.pk)]

        assert result == expected_response

    def test_execute__invalid_data__return_error(self, domain_services):
        with pytest.raises(PrimaryKeyError):
            domain_services.document().batch_delete(["some_string"])

    def test_execute__parent_and_child__return_success(self, domain_services, uow):
        parent_doc = DocumentEntityFactory(pk="1")
        child_doc = DocumentEntityFactory(pk="2")
        uow.document.get.return_value = parent_doc
        uow.document.get_descendants.return_value = [child_doc]

        result = domain_services.document().batch_delete([parent_doc.pk, child_doc.pk])
        expected_response = [DocumentEntityPk(child_doc.pk), DocumentEntityPk(parent_doc.pk)]

        assert result == expected_response
