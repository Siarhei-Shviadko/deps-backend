import pytest

from tests.factories import DocumentEntityFactory, DocumentMetadataFactory


@pytest.fixture
def document_fixture(uow):
    return uow.document.add(DocumentEntityFactory())


@pytest.fixture
def metadata_fixture(uow, document_fixture):
    return uow.document.upsert_document_metadata(DocumentMetadataFactory(document_id=document_fixture.pk))


class TestDocumentMetadata:
    def test_get_document_metadata__exists__return_200(self, client, metadata_fixture):
        response = client.get(f"/api/document/v1/documents/{metadata_fixture.document_id}/metadata")
        response_json = response.json()

        assert response.status_code == 200
        assert response_json["id"] == metadata_fixture.document_id
        assert response_json["metadata"] == metadata_fixture.metadata

    def test_get_document_metadata__not_exists__return_200_empty_dict(self, client):
        document_id = "999"
        response = client.get(f"/api/document/v1/documents/{document_id}/metadata")
        response_json = response.json()

        assert response.status_code == 200
        assert response_json["id"] == document_id
        assert response_json["metadata"] == {}
