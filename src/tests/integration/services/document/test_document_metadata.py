import pytest

from deps_documents.domain.exceptions import DocumentMetadataNotFoundError
from tests.factories.document_entity import (
    CommunicationEntityFactory,
    DocumentEntityFactory,
)


@pytest.fixture
def document_entity():
    yield DocumentEntityFactory(pk="1", communication=CommunicationEntityFactory(comments=[]))


class TestDocumentMetadata:
    def test_upsert_document_metadata(self, uow, domain_services, document_metadata, document_entity):
        document_metadata.document_id = document_entity.pk
        domain_services.document().create(document_entity)

        added_metadata = domain_services.document().upsert_document_metadata(document_metadata)

        assert added_metadata == document_metadata

    def test_get_document_metadata__metadata_exists__get_metadata(self, uow, domain_services, document_metadata, document_entity):
        document_metadata.document_id = document_entity.pk
        domain_services.document().create(document_entity)
        added_metadata = uow.document.upsert_document_metadata(document_metadata)

        retrieved_metadata = domain_services.document().get_document_metadata(added_metadata.document_id)
        assert retrieved_metadata == document_metadata

    def test_get_document_metadata__metadata_is_not_exist__get_empty_dict(
        self, uow, domain_services, document_metadata, document_entity
    ):
        retrieved_metadata = domain_services.document().get_document_metadata(document_entity.pk)
        assert retrieved_metadata.metadata == {}

    def test_delete_document_metadata(self, domain_services, uow, document_metadata, document_entity):
        document_metadata.document_id = document_entity.pk
        domain_services.document().create(document_entity)

        uow.document.upsert_document_metadata(document_metadata)
        retrieved_metadata = domain_services.document().get_document_metadata(document_metadata.document_id)
        assert retrieved_metadata == document_metadata

        domain_services.document().delete_document_metadata(document_metadata)
        retrieved_metadata = domain_services.document().get_document_metadata(document_metadata.document_id)
        assert retrieved_metadata.metadata == {}
