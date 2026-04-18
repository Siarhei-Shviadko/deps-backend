import pytest

from deps_documents.domain.exceptions import DocumentAlreadyHasDocumentType
from tests.factories import DocumentEntityFactory


def test_set_up_document_type__successful(uow, domain_services):
    document_repository = uow.document
    d1 = uow.document.add(DocumentEntityFactory(document_type=None))
    doc_type = "TestType"

    domain_services.document()._set_up_document_type([d1.pk], doc_type)
    updated_document = domain_services.document().get(d1.pk)

    assert updated_document.document_type == doc_type


def test_set_up_document_type__document_has_doc_type__error(uow, domain_services):
    document_repository = uow.document

    d1 = uow.document.add(DocumentEntityFactory(document_type="TestType"))
    with pytest.raises(DocumentAlreadyHasDocumentType):
        domain_services.document()._set_up_document_type([d1.pk], type_code="SetUpMe")
