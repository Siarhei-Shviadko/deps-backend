from deps_documents.domain.entities import LabelEntity


class TestCreateLabelIntegrity:
    def test_request__valid_data__valid_response(self, client, uow):
        label_name = "Test label"

        uow.label.add(LabelEntity(name=label_name))
        response = client.get("/api/document/v1/labels")
        response_json = response.json()

        assert response_json[0]["name"] == label_name
