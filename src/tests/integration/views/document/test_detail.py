import json
from http import HTTPStatus

from deps_documents.domain.constants import ContainerTypesEnum
from deps_documents.domain.entities import ContainerEmailMetadata
from tests.factories import DocumentEntityFactory
from tests.serializers import dump_document_for_request

from .utils import check_document_response_fields


class TestDocumentDetailView:
    @classmethod
    def setup_class(cls):
        cls.document_entity = DocumentEntityFactory()
        cls.total_entities = 10
        cls.document_entities = DocumentEntityFactory.create_batch(cls.total_entities)
        cls.data = dump_document_for_request(DocumentEntityFactory())

    def test_get__existing_document__return_document(self, client, uow):
        document_entity = DocumentEntityFactory()
        document = uow.document.add(document_entity)

        response = client.get(f"/api/document/v1/documents/{document.pk}")

        assert response.status_code == 200

    def test_get__existing_document__return_proper_document_fields(self, client, uow):
        document_entity = DocumentEntityFactory()
        document = uow.document.add(document_entity)

        response = client.get(f"/api/document/v1/documents/{document.pk}")
        document_json = response.json()
        check_document_response_fields(document_json)

    def test_get__not_existing__raise_document_not_found(self, client):
        response = client.get("/api/document/v1/documents/123")

        assert response.status_code == 404

    def test_get__not_existing_document_undefined__return_false(self, client):
        response = client.get("/api/document/v1/documents/undefined")

        assert response.status_code == 400

    def test_delete__existing_document__return_true(self, client, uow):
        document_entity = DocumentEntityFactory()
        document = uow.document.add(document_entity)

        response = client.delete(f"/api/document/v1/documents/{document.pk}")

        assert response.status_code == 200

    def test_delete__not_existing_document__return_false(self, client):
        response = client.delete("/api/document/v1/documents/123")

        assert response.status_code == 404

    def test_delete__not_existing_document_undefined__return_false(self, client):
        response = client.delete("/api/document/v1/documents/undefined")

        assert response.status_code == 400

    def test_get__container_document__return_first_level_child_count(self, client, uow):
        parent = uow.document.add(
            DocumentEntityFactory(container_type=ContainerTypesEnum.EMAIL, container_metadata=ContainerEmailMetadata())
        )
        uow.document.add(DocumentEntityFactory(parent_id=parent.pk))

        response = client.get(f"/api/document/v1/documents/{parent.pk}")
        response_data = response.json()

        assert response_data["containerMetadata"]["firstLevelChildCount"] == 1

    def test_put__valid_document__return_200_response(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]
        uow.document.add(self.document_entity)
        response = client.get("/api/document/v1/documents")
        response_json = response.json()
        pk = response_json["result"][0]["_id"]

        document = self.document_entity
        ser_document = dump_document_for_request(document)
        doc = {"document": {**ser_document}}

        doc = json.dumps(doc)

        response = client.put(f"/api/document/v1/documents/{pk}", data=doc)

        assert response.status_code == 200

    def test_put__valid_document__return_doc_id(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]
        uow.document.add(self.document_entity)

        response = client.get("/api/document/v1/documents")
        response_json = response.json()
        pk = response_json["result"][0]["_id"]

        document = self.document_entity
        ser_document = dump_document_for_request(document)
        doc = {"document": {**ser_document}}

        doc = json.dumps(doc)

        response = client.put(f"/api/document/v1/documents/{pk}", data=doc)
        response_json = response.json()

        assert "_id" in response_json

    def test_put__not_valid_document_id__return_404_response(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]
        uow.document.add(self.document_entity)

        document = self.document_entity
        ser_document = dump_document_for_request(document)
        doc = {"document": {**ser_document}}

        doc = json.dumps(doc)

        response = client.put("/api/document/v1/documents/1000", data=doc)

        assert response.status_code == 404

    def test_put__changing_document__changes_document(self, client, uow):
        document = uow.document.add(self.document_entity)
        pk = document.pk

        ser_document = dump_document_for_request(document)
        doc = {"document": {**ser_document}}

        new_title = "Modified " + doc["document"]["title"]
        doc["document"]["title"] = new_title
        doc = json.dumps(doc)

        client.put(f"/api/document/v1/documents/{pk}", data=doc)
        saved_doc = uow.document.get(pk)
        assert saved_doc.title == new_title

    def test_patch__valid_request__return_ok(self, client, uow):
        document = uow.document.add(DocumentEntityFactory())
        data = dump_document_for_request(DocumentEntityFactory())

        for field, value in data.items():
            req_data = json.dumps({"document": {field: value}})
            response = client.patch(f"/api/document/v1/documents/{document.pk}", data=req_data)

            assert response.status_code == HTTPStatus.OK
