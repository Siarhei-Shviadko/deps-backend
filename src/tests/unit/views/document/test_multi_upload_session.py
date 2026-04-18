from deps_documents.domain.dtos import UseCaseResponseObject
from deps_documents.domain.use_cases.batch_upload.create_upload_session_data import (
    ResponseObject,
)


class TestMultiUploadSessionView:
    def test_post__valid_request__return_200(self, client, use_cases_mock):
        res = UseCaseResponseObject.build_success(ResponseObject(batch_id="1"))
        use_cases_mock.create_upload_session().execute.return_value = res
        response = client.post("/api/document/v1/documents/multi-upload-session")

        assert response.status_code == 200

    def test_post__valid_request__return_batch_id(self, client, use_cases_mock):
        res = UseCaseResponseObject.build_success(ResponseObject(batch_id="1"))
        use_cases_mock.create_upload_session().execute.return_value = res
        response = client.post("/api/document/v1/documents/multi-upload-session")
        response_json = response.json()

        assert response_json["batchId"] == "1"
