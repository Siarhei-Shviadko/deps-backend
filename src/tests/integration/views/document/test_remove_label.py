from deps_documents.domain.entities import LabelEntity
from tests.factories import DocumentEntityFactory


class TestDocumentRemoveLabelIntegrity:
    def test_request__valid_data__valid_response(self, client, uow):
        document = uow.document.add(DocumentEntityFactory(labels=None))
        label = uow.label.add(LabelEntity("Test label"))
        uow.document.add_label(label.pk, [document.pk])

        response = client.post("api/document/v1/documents/remove-label", json={"documentId": document.pk, "labelId": label.pk})
        response_json = response.json()

        assert response_json
