from http import HTTPStatus
from uuid import uuid4

from deps_documents.domain.entities import DocumentTypeEntity


class TestCreateDocument:
    base_url = "/api/document/v1/documents/create-document"

    def test_create_document__document_type_exists__success(self, client, uow, user_fixture, set_test_user):
        document_name = "test"
        document_type = DocumentTypeEntity(id=uuid4().hex, tenant=user_fixture["organisation"], name=uuid4().hex)
        engine = "TESSERACT"
        language = "eng"
        files = ["test.png"]
        assign_to_me = True

        payload = {
            "documentName": document_name,
            "documentTypeId": document_type.id,
            "engine": engine,
            "language": language,
            "files": files,
            "assignToMe": assign_to_me,
        }
        uow.document_type.save(document_type)

        response = client.post(url=self.base_url, json=payload)

        assert response.status_code == HTTPStatus.OK

        document_id = response.json()["documentId"]
        created_document = uow.document.get(document_id)

        assert created_document.title == document_name
        assert created_document.document_type == document_type.id
        assert created_document.engine == engine
        assert created_document.language == language
        assert created_document.files[0].blob_name == files[0]
        assert created_document.reviewer.id == user_fixture["subject"]

    def test_create_document__document_type_does_not_exist__failure(self, client):
        document_name = "test"
        files = ["test.png"]

        payload = {
            "documentName": document_name,
            "documentTypeId": uuid4().hex,
            "files": files,
        }

        response = client.post(url=self.base_url, json=payload)

        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_create_document__document_type_is_none__success(self, client, uow):
        document_name = "test"
        files = ["test.png"]

        payload = {
            "documentName": document_name,
            "files": files,
        }

        response = client.post(url=self.base_url, json=payload)

        assert response.status_code == HTTPStatus.OK

        document_id = response.json()["documentId"]
        created_document = uow.document.get(document_id)

        assert created_document.title == document_name
        assert created_document.document_type is None
        assert created_document.engine is None
        assert created_document.language is None
        assert created_document.files[0].blob_name == files[0]
        assert created_document.reviewer is None
