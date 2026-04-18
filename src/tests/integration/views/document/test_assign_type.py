from operator import itemgetter

from deps_documents.domain.constants import DocumentStateEnum
from tests.factories import DocumentEntityFactory


class TestDocumentAssignTypeView:
    def test_document_assign_type__valid_input__200(self, client, uow):
        document_repository = uow.document

        d2 = document_repository.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED))

        params = {"documentIds": [d2.pk], "typeName": "TestType"}

        response = client.post("/api/document/v1/documents/assign-type", json=params)
        response_content = response.json()

        expected_update_list = {d2.pk}

        assert response.status_code == 200
        assert set(map(itemgetter("_id"), response_content)) == expected_update_list

    def test_document_assign_type__invalid_input__422(self, client):
        params = {
            "Invalid": 1,
        }

        response = client.post("/api/document/v1/documents/assign-type", json=params)

        assert response.status_code == 422

    def test_document_assign_type__invalid_document_ids__400(self, client, uow):
        document_repository = uow.document

        for _ in range(3):
            document_repository.add(DocumentEntityFactory())

        params = {"documentIds": ["one", "two"], "typeName": "TestType"}

        response = client.post("/api/document/v1/documents/assign-type", json=params)

        assert response.status_code == 400

    def test_document_assign_type__empty_ids_list__422(self, client):
        params = {"documentIds": [], "typeName": "Name"}

        response = client.post("/api/document/v1/documents/assign-type", json=params)

        assert response.status_code == 422

    def test_document_assign_type__empty_type_name__422(self, client):
        params = {"documentIds": ["1", "2", "3"], "typeName": ""}

        response = client.post("/api/document/v1/documents/assign-type", json=params)

        assert response.status_code == 422

    def test_document_assign_type__invalid_json__422(self, client):
        params = '"invalid json syntax('

        response = client.post("/api/document/v1/documents/assign-type", data=params)

        assert response.status_code == 422

    def test_document_assign_type_type_name_none__200(self, client, uow):
        document_ids = [str(i) for i in range(1, 4)]
        documents = [DocumentEntityFactory(pk=document_id, state=DocumentStateEnum.COMPLETED) for document_id in document_ids]
        for document in documents:
            uow.document.add(document)

        params = {"documentIds": ["1", "2", "3"], "typeName": None}

        response = client.post("/api/document/v1/documents/assign-type", json=params)
        assert response.status_code == 200
