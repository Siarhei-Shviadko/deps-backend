from deps_documents.domain.entities import LabelEntity


class TestLabelView:
    def test_post__valid_body__return_200_response(self, client, label_service_mock):
        label_pk = "1"
        label_name = "Test label"
        label_service_mock.create.return_value = LabelEntity(pk=label_pk, name=label_name)

        response = client.post("/api/document/v1/labels", json={"labelName": label_name})

        assert response.status_code == 200

    def test_post__valid_body__return_proper_response_fields_value(self, client, label_service_mock):
        label_name = "Test label"
        label_pk = "1"

        label_service_mock.create.return_value = LabelEntity(name=label_name, pk=label_pk)

        response = client.post("/api/document/v1/labels", json={"labelName": label_name})
        response_json = response.json()

        assert response_json == {"_id": label_pk, "name": label_name}

    def test_post__null_label_name__return_422_response(self, client):
        response = client.post("/api/document/v1/labels")

        assert response.status_code == 422

    def test_post__empty_label_name__return_422_response(self, client):
        response = client.post("/api/document/v1/labels", json={"labelName": ""})

        assert response.status_code == 422

    def test_get__return_200_response(self, client, label_service_mock):
        label_name = "Test label"
        label_service_mock.get_list.return_value = [LabelEntity(label_name)]

        response = client.get("/api/document/v1/labels")

        assert response.status_code == 200

    def test_get__return_proper_response_fields_value(self, client, label_service_mock):
        label_name = "Test label"
        label_pk = "1"
        label_service_mock.get_list.return_value = [LabelEntity(name=label_name, pk=label_pk)]
        expected_json = [{"name": label_name, "_id": label_pk}]

        response = client.get("/api/document/v1/labels")
        response_json = response.json()

        assert response_json == expected_json
