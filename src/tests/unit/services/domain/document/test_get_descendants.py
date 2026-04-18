import pytest

from tests.factories.document_entity import DocumentEntityFactory


class TestDocumentServiceGetDescendants:
    def test_execute__valid_data__response_documents_list(self, uow, domain_services):
        document_entity = DocumentEntityFactory(pk="1")
        document_entity_descendant = DocumentEntityFactory(parent_id=document_entity.pk)
        uow.document.get_descendants.return_value = [document_entity_descendant]
        result = domain_services.document().get_descendants("1")

        assert result == [document_entity_descendant]
