import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.exceptions import DocumentAlreadyHasDocumentType
from tests.factories import DocumentEntityFactory


def test_set_up_doc_type__doc_has_type__error(uow, domain_services):
    document = DocumentEntityFactory(document_type="TestType")
    doc_type = "ChangeMe"
    uow.document.select_for_update.return_value = [document]

    with pytest.raises(DocumentAlreadyHasDocumentType):
        domain_services.document()._set_up_document_type([document.pk], doc_type)


def test_set_up_doc_type__no_errors(uow, domain_services):
    document = DocumentEntityFactory(document_type=None)
    doc_type = "ChangeMe"
    uow.document.select_for_update.return_value = [document]

    domain_services.document()._set_up_document_type([document.pk], doc_type)
