import pytest

from deps_documents.domain.exceptions import (
    DocumentMetadataNotFoundError,
    DocumentNotFoundError,
)
from tests.factories.document_entity import (
    CommunicationEntityFactory,
    DocumentEntityFactory,
)


@pytest.fixture
def document_entity():
    yield DocumentEntityFactory(pk="1", communication=CommunicationEntityFactory(comments=[]))


class TestDocumentMetadata:
    def test_upsert_document_metadata__document_exists__success(self, uow, document_metadata, document_entity):
        document_metadata.document_id = document_entity.pk
        uow.document.add(document_entity)

        added_metadata = uow.document.upsert_document_metadata(document_metadata)
        assert added_metadata == document_metadata

    def test_upsert_document_metadata__document_does_not_exist__error_raised(self, uow, document_metadata, document_entity):
        with pytest.raises(DocumentNotFoundError):
            uow.document.upsert_document_metadata(document_metadata)

    def test_upsert_document_metadata__metadata_already_exists__new_metadata_saved(self, uow, document_metadata, document_entity):
        document_metadata.document_id = document_entity.pk
        uow.document.add(document_entity)

        old_metadata = uow.document.upsert_document_metadata(document_metadata)
        assert old_metadata == document_metadata

        document_metadata.metadata = {"new_parameter": "awesome_data"}
        new_metadata = uow.document.upsert_document_metadata(document_metadata)
        assert new_metadata == document_metadata

    def test_get_document_metadata__metadata_exists__success(self, uow, document_metadata, document_entity):
        document_metadata.document_id = document_entity.pk
        uow.document.add(document_entity)
        added_metadata = uow.document.upsert_document_metadata(document_metadata)

        retrieved_metadata = uow.document.get_document_metadata(added_metadata.document_id)
        assert retrieved_metadata == document_metadata

    def test_get_document_metadata__metadata_does_not_exist__error_raised(self, uow, document_metadata):
        with pytest.raises(DocumentMetadataNotFoundError):
            uow.document.get_document_metadata(document_metadata.document_id)

    def test_delete_document_metadata__success(self, uow, document_metadata, document_entity):
        document_metadata.document_id = document_entity.pk
        uow.document.add(document_entity)
        uow.document.upsert_document_metadata(document_metadata)

        assert uow.document.get_document_metadata(document_metadata.document_id)

        uow.document.delete_document_metadata(document_metadata)
        with pytest.raises(DocumentMetadataNotFoundError):
            uow.document.get_document_metadata(document_metadata.document_id)
