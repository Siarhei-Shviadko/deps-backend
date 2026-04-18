from deps_documents import constants


class TestHealthcheck:
    endpoint = constants.BASE_API_PREFIX

    def test_healthcheck_endpoint_return_200(self, postgres_datasource_mock, client):
        postgres_datasource_mock.healthcheck.return_value = "All good!!!"
        response = client.get(f"{self.endpoint}/healthcheck")

        assert response.status_code == 200

    def test_healthcheck_endpoint_return_503(self, postgres_datasource_mock, client):
        postgres_datasource_mock.healthcheck.side_effect = Exception("Service unavailable")
        response = client.get(f"{self.endpoint}/healthcheck")

        assert response.status_code == 503
