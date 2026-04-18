from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.entities import DocumentEntity
from tests.factories.document_entity import DocumentEntityFactory


class TestDocumentServiceCompleteReview:
    def test_execute__valid_data__response_value_document(self, uow, domain_services):
        document = DocumentEntityFactory(state=DocumentStateEnum.IN_REVIEW)
        uow.document.select_for_update.return_value = [document]
        uow.document.update.return_value = document

        result = domain_services.document().complete_review(document.pk)
        assert isinstance(result, DocumentEntity)

    def test_execute__valid_data__document_sent_for_validation(self, uow, domain_services, services):
        document = DocumentEntityFactory(state=DocumentStateEnum.IN_REVIEW)
        uow.document.select_for_update.return_value = [document]
        uow.document.update.return_value = document

        domain_services.document().complete_review(document.pk)

        services.validation().send_document_to_validation.assert_called_with(document.pk)
