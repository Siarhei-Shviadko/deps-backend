class TestMultiUploadSessionView:
    def test_post__create_upload_session__response_status_200(self, client):
        response = client.post("/api/document/v1/documents/multi-upload-session")

        assert response.status_code == 200

    def test_post__create_upload_session__response_not_empty(self, client):
        response = client.post("/api/document/v1/documents/multi-upload-session")

        assert response.json()["batchId"]
