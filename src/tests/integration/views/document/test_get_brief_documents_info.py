from http import HTTPStatus

from tests.factories import DocumentEntityFactory


class TestGetBriefDocumentsInfo:
    base_url = "/api/document/v1/brief-documents-info"

    def test_get_one_document__document_exists(self, client, uow):
        document = uow.document.add(DocumentEntityFactory())

        response = client.get(f"{self.base_url}?documentIds={document.pk}")

        assert response.status_code == HTTPStatus.OK

        response_json = response.json()

        assert response_json["documents"]
        assert response_json["documents"][0]["state"] == document.state.value
        assert response_json["documents"][0]["title"] == document.title
        assert response_json["documents"][0]["typeId"] == document.document_type
        assert response_json["documents"][0]["engine"] == document.engine
        assert response_json["documents"][0]["language"] == document.language
        assert response_json["documents"][0]["files"][0] == document.files[0].blob_name
        assert response_json["documents"][0]["errorInState"] == document.error.in_state

    def test_get_one_document__document_does_not_exist(self, client, uow):
        response = client.get(f"{self.base_url}?documentIds=3")

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_multiple_documents__documents_exist(self, client, uow):
        documents = [uow.document.add(document) for document in DocumentEntityFactory.create_batch(3)]

        query = "&".join([f"documentIds={document.pk}" for document in documents])
        response = client.get(f"{self.base_url}?{query}")

        assert response.status_code == HTTPStatus.OK

        response_json = response.json()

        assert response_json["documents"]
