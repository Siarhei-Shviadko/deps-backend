from deps_documents.domain.constants import DocumentStateEnum
from tests.factories import DocumentEntityFactory


class TestRunPipelineView:
    def test_post__valid_input__200(self, client, uow):
        document_ids = [str(i) for i in range(1, 6)]
        documents = [DocumentEntityFactory(pk=document_id, state=DocumentStateEnum.NEW) for document_id in document_ids]
        for document in documents:
            uow.document.add(document)

        updated_documents_ids = [document.pk for document in documents if document.state == DocumentStateEnum.NEW]

        params = {"documentIds": document_ids, "engineName": "TESSERACT"}

        response = client.post("/api/document/v1/documents/run-pipeline", json=params)
        response_content = response.json()

        assert response.status_code == 200
        assert sorted(d["_id"] for d in response_content) == sorted(updated_documents_ids)

    def test_post__wrong_state_return__400(self, client, uow):
        document_ids = [str(i) for i in range(1, 3)]
        documents = [DocumentEntityFactory(pk=document_id, state=DocumentStateEnum.COMPLETED) for document_id in document_ids]
        for document in documents:
            uow.document.add(document)

        params = {"documentIds": document_ids, "engineName": "TESSERACT"}

        response = client.post("/api/document/v1/documents/run-pipeline", json=params)

        assert response.status_code == 400

    def test_post__document_not_exists__return_404(self, client):
        response = client.post("/api/document/v1/documents/run-pipeline", json={"documentIds": ["1"], "engineName": "TESSERACT"})
        assert response.status_code == 404

    def test_post__invalid_input__422(self, client):
        params = {
            "Invalid": 1,
        }

        response = client.post("/api/document/v1/documents/run-pipeline", json=params)

        assert response.status_code == 422

    def test_post__empty_ids_list__422(self, client):
        params = {"documentIds": [], "engineName": "TESSERACT"}

        response = client.post("/api/document/v1/documents/run-pipeline", json=params)

        assert response.status_code == 422

    def test_post__invalid_json__422(self, client):
        params = '"invalid json syntax('

        response = client.post("/api/document/v1/documents/run-pipeline", data=params)

        assert response.status_code == 422
