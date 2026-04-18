import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.exceptions import DocumentStateError
from tests.factories import DocumentEntityFactory


class TestRunPipelineUseCase:
    def test_execute__one_document_in_new_state__asserts_pass(self, domain_services, uow):
        uow.document.find_by_pks.return_value = [DocumentEntityFactory(pk="1", state=DocumentStateEnum.NEW)]

        result = domain_services.document().run_pipeline([], engine="TESSERACT")

        assert len(result) == 1

    def test_execute__mixed_input__asserts_pass(self, domain_services, uow):
        document_ids = [str(i) for i in range(5)]
        uow.document.find_by_pks.return_value = [
            DocumentEntityFactory(pk=document_id, state=DocumentStateEnum.NEW) for document_id in document_ids
        ]
        updated_documents_ids = [
            document.pk for document in domain_services.document().run_pipeline(document_ids, engine="TESSERACT")
        ]
        invalid_documents_ids = ["100", "document_id"]

        result = domain_services.document().run_pipeline(document_ids + invalid_documents_ids, engine="TESSERACT")

        documents_ids = [documents.pk for documents in result]

        assert sorted(documents_ids) == sorted(updated_documents_ids)

    def test_execute__document_wrong_state__raises_error(self, domain_services, uow):
        document_ids = [str(i) for i in range(1, 3)]
        documents = [DocumentEntityFactory(pk=document_id, state=DocumentStateEnum.COMPLETED) for document_id in document_ids]

        uow.document.find_by_pks.return_value = documents

        with pytest.raises(DocumentStateError):
            domain_services.document().run_pipeline(document_ids, engine="TESSERACT")
