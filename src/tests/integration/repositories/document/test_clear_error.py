import pytest

from deps_documents.domain.exceptions import PrimaryKeyError
from tests.factories import DocumentEntityFactory, ErrorEntityFactory


class TestCaseDocumentEntityRepositoryClearError:
    def test_clear_error__existing_doc__return_true(self, uow):
        document = uow.document.add(DocumentEntityFactory())
        response = uow.document.clear_error(document.pk)

        assert response

    def test_clear_error__existing_doc__error_cleared(self, uow):
        document = uow.document.add(DocumentEntityFactory(error=ErrorEntityFactory()))
        uow.document.clear_error(document.pk)
        response = uow.document.get(document.pk)

        assert response.error is None

    def test_clear_error__not_existing_doc__return_false(self, uow):
        response = uow.document.clear_error("1")

        assert not response

    def test_clear_error__not_valid_document_pk__raises_primary_key_error(self, uow):
        with pytest.raises(PrimaryKeyError):
            uow.document.clear_error("a")
