import pytest

from tests.factories import DocumentEntityFactory


@pytest.fixture
def run_pipeline_from_step_mock(document_service_mock):
    document_service_mock.run_pipeline_from_step.return_value = [DocumentEntityFactory(labels=None)]


@pytest.mark.usefixtures("run_pipeline_from_step_mock")
class TestRunPipelineFromStepView:
    def test_post__all_valid_params__return_200(self, client):
        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step",
            json={"documentIds": ["1"], "step": "extraction", "engineName": "TESSERACT"},
        )
        assert response.status_code == 200

    def test_post__missing_engine__return_200(self, client):
        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step", json={"documentIds": ["1"], "step": "extraction"}
        )
        assert response.status_code == 200

    def test_post__invalid_step__return_422(self, client):
        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step",
            json={"documentIds": ["1"], "step": "invalidStepName", "engineName": "TESSERACT"},
        )
        assert response.status_code == 422

    def test_post__missing_step__return_422(self, client):
        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step", json={"documentIds": ["1"], "engineName": "TESSERACT"}
        )
        assert response.status_code == 422

    def test_post__missing_document_ids__return_422(self, client):
        response = client.post(
            "/api/document/v1/documents/run-pipeline-from-step", json={"step": "extraction", "engineName": "TESSERACT"}
        )
        assert response.status_code == 422
