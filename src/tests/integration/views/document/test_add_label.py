from deps_documents.domain.entities import LabelEntity
from tests.factories import DocumentEntityFactory


class TestDocumentAddLabelIntegrity:
    def test_request__valid_data__valid_response(self, client, uow):
        document = uow.document.add(DocumentEntityFactory(labels=None))
        label = uow.label.add(LabelEntity("Test label"))

        expected_json = {"updatedDocuments": [{"_id": document.pk, "title": ""}]}

        response = client.post("/api/document/v1/documents/add-label", json={"documentIds": [document.pk], "labelId": label.pk})
        response_json = response.json()

        assert response_json[0]["_id"] == expected_json["updatedDocuments"][0]["_id"]
