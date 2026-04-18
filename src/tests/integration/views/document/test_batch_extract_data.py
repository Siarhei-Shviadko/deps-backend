import pytest

from tests.factories import DocumentEntityFactory


class TestBatchExtractDataView:
    def test_post__invalid_error__400(self, client, uow):
        document_ids = [str(i) for i in range(2)]
        documents = [DocumentEntityFactory(pk=document_id) for document_id in document_ids]
        for document in documents:
            uow.document.add(document)

        params = {"documentIds": ["1", "600"]}

        response = client.post("/api/document/v1/documents/extract-data", json=params)
        assert response.status_code == 404

        response_content = response.json()

        assert "1" not in response_content["message"]
        assert "600" in response_content["message"]

    def test_post__pk_error__400(self, client, uow):
        document_ids = [str(i) for i in range(2)]
        documents = [DocumentEntityFactory(pk=document_id) for document_id in document_ids]
        for document in documents:
            uow.document.add(document)

        params = {"documentIds": ["1", "test_id"]}

        response = client.post("/api/document/v1/documents/extract-data", json=params)
        assert response.status_code == 400

        response_content = response.json()
        assert "test_id" in response_content["message"]

    @pytest.mark.skip
    def test_post__data_extract_error__400(self, client, uow):
        document_ids = [str(i) for i in range(1, 3)]
        for document_id in document_ids:
            uow.document.add(DocumentEntityFactory(pk=document_id, document_type="Code"))
        params = {"documentIds": ["1", "2"]}

        response = client.post("/api/document/v1/documents/extract-data", json=params)
        assert response.status_code == 400

        response_content = response.json()
        assert "1" in response_content["message"]
