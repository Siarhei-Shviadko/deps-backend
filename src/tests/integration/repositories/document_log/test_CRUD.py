import pytest

from deps_documents.domain.exceptions import DocumentNotFoundError
from tests.factories import DocumentEntityFactory, DocumentLogEntityFactory


class TestCaseDocumentLogEntityRepositoryCRUD:
    @classmethod
    def setup_class(cls):
        cls.document_entity = DocumentEntityFactory()
        cls.document_entity1 = DocumentEntityFactory()

    def test_create__new_document_log__return_document_log(self, uow):
        document = uow.document.add(self.document_entity)
        document_log_entity = DocumentLogEntityFactory(document_id=document.pk)
        result = uow.document_log.add(document_log_entity)
        assert result.pk is not None

    def test_create__new_document_log__return_document_log_document_not_exists(self, uow):
        document_log_entity = DocumentLogEntityFactory()
        with pytest.raises(DocumentNotFoundError):
            uow.document_log.add(document_log_entity)

    def test_get_document_logs__document_exist__return_documents(self, uow):
        document = uow.document.add(self.document_entity)
        document1 = uow.document.add(self.document_entity1)

        document_log_entity = DocumentLogEntityFactory(document_id=document.pk)
        document_log_entity1 = DocumentLogEntityFactory(document_id=document.pk)
        document_log_entity2 = DocumentLogEntityFactory(document_id=document1.pk)

        document_log = uow.document_log.add(document_log_entity)
        document_log1 = uow.document_log.add(document_log_entity1)
        uow.document_log.add(document_log_entity2)

        result = uow.document_log.get_document_logs(document_id=document.pk)
        assert [r.pk for r in result] == [document_log.pk, document_log1.pk]

    def test_get_document_logs__document_not_exist__raise_document_not_found(self, uow):
        with pytest.raises(DocumentNotFoundError):
            uow.document_log.get_document_logs(document_id="1839")
