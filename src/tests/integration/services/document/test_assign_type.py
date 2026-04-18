import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.exceptions import DocumentAlreadyHasDocumentType
from tests.factories import DocumentEntityFactory


class TestDocumentServiceAssignType:
    def test_execute__list_of_documents_input__asserts_pass(self, uow, domain_services):
        document_repository = uow.document

        d1 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED))
        d2 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED))

        result = domain_services.document().assign_type([d1.pk, d2.pk], "TestType")

        assert result[0].pk == d1.pk
        assert result[1].pk == d2.pk

    def test_batch_update__type_is_none__success_response(self, uow, domain_services):
        document_repository = uow.document

        d1 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.IN_REVIEW))

        result = domain_services.document().assign_type([d1.pk], type_code=None)

        assert result[0].pk == d1.pk

    def test_assign_type__initial_true__successful(self, uow, domain_services):
        document_repository = uow.document
        d1 = uow.document.add(DocumentEntityFactory(document_type=None))
        doc_type = "TestType"

        domain_services.document().assign_type([d1.pk], doc_type, initial_assign=True)
        updated_document = domain_services.document().get(d1.pk)

        assert updated_document.document_type == doc_type

    def test_assign_type__initial_true_document_has_doc_type__error(self, uow, domain_services):
        document_repository = uow.document

        d1 = uow.document.add(DocumentEntityFactory(document_type="TestType"))
        with pytest.raises(DocumentAlreadyHasDocumentType):
            domain_services.document().assign_type([d1.pk], type_code="SetUpMe", initial_assign=True)
