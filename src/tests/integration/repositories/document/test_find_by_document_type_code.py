from tests.factories import DocumentEntityFactory


class TestCaseDocumentEntityRepositoryFindByDocumentTypeCode:
    def test_no_documents__retun_empty_list(self, uow):
        assert len(uow.document.find_by_document_type_code("BelarusPassport")) == 0

    def test_no_documents_of_type__return_empty_list(self, uow):
        doc_entity = DocumentEntityFactory(document_type="DirectionalSurvey", title="Some document")
        uow.document.add(doc_entity)

        assert len(uow.document.find_by_document_type_code("BelarusPassport")) == 0

    def test_documents_exist__return_list(self, uow):
        uow.document.add(DocumentEntityFactory(document_type="DirectionalSurvey"))
        uow.document.add(DocumentEntityFactory(document_type="BelarusPassport"))
        uow.document.add(DocumentEntityFactory(document_type="BelarusPassport"))

        assert len(uow.document.find_by_document_type_code("BelarusPassport")) == 2
