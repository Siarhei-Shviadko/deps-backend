import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.exceptions import PrimaryKeyError
from tests.factories import DocumentEntityFactory


class TestCaseDocumentEntityRepositoryUpdateState:
    def test_update_state__existing_doc__return_true(self, uow):
        document = uow.document.add(DocumentEntityFactory())
        response = uow.document.update_state(document.pk, DocumentStateEnum.IDENTIFICATION)

        assert response

    def test_update_state__existing_doc__update_state(self, uow):
        document = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.NEW))
        uow.document.update_state(document.pk, DocumentStateEnum.IDENTIFICATION)

        response = uow.document.get(document.pk)

        assert response.state == DocumentStateEnum.IDENTIFICATION

    def test_update_state__not_existing_doc__return_false(self, uow):
        response = uow.document.update_state("1", DocumentStateEnum.IDENTIFICATION)

        assert not response

    def test_update_state__not_valid_document_pk__raises_primary_key_error(self, uow):
        with pytest.raises(PrimaryKeyError):
            uow.document.update_state("a", DocumentStateEnum.IDENTIFICATION)
