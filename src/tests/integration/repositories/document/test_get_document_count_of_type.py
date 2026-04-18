from tests.factories import DocumentEntityFactory


class TestCaseDocumentGetDocumentCountOfType:
    def test__no_documents_exist__return_0(self, uow):
        assert uow.document.get_document_count_of_type("BelarusPassport") == 0

    def test__documents_exist__return_count(self, uow):
        uow.document.add(DocumentEntityFactory(document_type="DirectionalSurvey"))
        uow.document.add(DocumentEntityFactory(document_type="DirectionalSurvey"))

        assert uow.document.get_document_count_of_type("DirectionalSurvey") == 2
