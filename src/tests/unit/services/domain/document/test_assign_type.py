import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.exceptions import (
    DocumentAlreadyHasDocumentType,
    DocumentStateError,
)
from tests.factories import DocumentEntityFactory


class TestAssignTypeUseCase:
    def test_assign_type__document_wrong_state__raises_error(self, uow, domain_services):
        document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.NEW)

        doc_type = "TestDocType"

        uow.document.select_for_update.return_value = [document]

        with pytest.raises(DocumentStateError):
            domain_services.document().assign_type(document.pk, doc_type)

    def test_assign_type__initial_true_doc_has_type__error(self, uow, domain_services):
        document = DocumentEntityFactory(document_type="TestType")
        doc_type = "ChangeMe"
        uow.document.select_for_update.return_value = [document]

        with pytest.raises(DocumentAlreadyHasDocumentType):
            domain_services.document().assign_type([document.pk], doc_type, initial_assign=True)

    def test_set_up_doc_type__no_errors(self, uow, domain_services):
        document = DocumentEntityFactory(document_type=None)
        doc_type = "ChangeMe"
        uow.document.select_for_update.return_value = [document]

        domain_services.document().assign_type([document.pk], doc_type, initial_assign=True)
