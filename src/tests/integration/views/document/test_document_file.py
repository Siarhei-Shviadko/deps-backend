from datetime import datetime
from email.message import EmailMessage
from io import BytesIO

from deps_documents.domain.constants import DocumentStateEnum


class TestDocumentFileIntegrity:
    def test_post__upload_new_document_file__new_document_id(self, client):
        files = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
        }
        response = client.post("/api/document/v1/documents/document-file", files=files)

        response_json = response.json()

        assert response.status_code == 200
        assert "id" in response_json

    def test_post__upload_without_pipeline_run__new_document_with_the_new_state(self, client, uow):
        data = {"runPipeline": False}
        files = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
        }
        response = client.post("/api/document/v1/documents/document-file", data=data, files=files)

        response_json = response.json()

        assert response.status_code == 200
        assert "id" in response_json

        created_document = uow.document.get(response_json["id"])
        assert created_document.state == DocumentStateEnum.NEW

    def test_post__no_document_file__bad_request(self, client):
        response = client.post("/api/document/v1/documents/document-file", data={})

        assert response.status_code == 422

    def test_post__filename_passed__document_with_this_filename(self, client, uow):
        document_name = "document_name"
        files = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
        }
        data = {
            "runPipeline": False,
            "documentName": document_name,
        }
        response = client.post("/api/document/v1/documents/document-file", data=data, files=files)

        response_json = response.json()

        created_document = uow.document.get(response_json["id"])
        assert created_document.title == document_name

    def test_post__same_batch_id__files_added_to_same_document(self, client, uow):
        batch_id_response = client.post("api/document/v1/documents/multi-upload-session")
        batch_id = batch_id_response.json()["batchId"]
        files1 = {
            "file": ("document_file1.jpg", BytesIO(b"a new document file content1"), "application/jpg"),
        }
        data1 = {
            "runPipeline": False,
            "batchId": batch_id,
        }
        response1 = client.post("/api/document/v1/documents/document-file", data=data1, files=files1)

        document_id1 = response1.json()["id"]

        files2 = {
            "file": ("document_file2.jpg", BytesIO(b"a new document file content2"), "application/jpg"),
        }
        data2 = {
            "runPipeline": False,
            "batchId": batch_id,
        }
        response2 = client.post("/api/document/v1/documents/document-file", data=data2, files=files2)

        document_id2 = response2.json()["id"]

        assert document_id1 == document_id2

        created_document = uow.document.get(document_id1)
        assert len(created_document.files) == 2

    def test_post__different_batch_id__different_documents_created(self, client):
        batch_id_response_1 = client.post("/api/document/v1/documents/multi-upload-session")
        files1 = {
            "file": ("document_file1.jpg", BytesIO(b"a new document file content1"), "application/jpg"),
        }
        data1 = {
            "runPipeline": False,
            "batchId": batch_id_response_1.json()["batchId"],
        }
        response1 = client.post("/api/document/v1/documents/document-file", data=data1, files=files1)

        document_id1 = response1.json()["id"]

        batch_id_response_2 = client.post("/api/document/v1/documents/multi-upload-session")
        files2 = {
            "file": ("document_file2.jpg", BytesIO(b"a new document file content2"), "application/jpg"),
        }
        data2 = {
            "runPipeline": False,
            "batchId": batch_id_response_2.json()["batchId"],
        }
        response2 = client.post("/api/document/v1/documents/document-file", data=data2, files=files2)

        document_id2 = response2.json()["id"]

        assert document_id1 != document_id2

    def test_post__batch__no_session_initialized__response_status_404(self, client):
        data = {
            "runPipeline": False,
            "batchId": "some_random_batch_id",
        }

        files = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
        }

        response = client.post("/api/document/v1/documents/document-file", data=data, files=files)

        assert response.status_code == 404

    def test_post__batch__invalid_batch_id__response_status_404(self, client):
        client.post("/api/document/v1/documents/multi-upload-session")
        data = {
            "runPipeline": False,
            "batchId": "some_random_batch_id",
        }
        files = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
        }
        response = client.post("/api/document/v1/documents/document-file", data=data, files=files)

        assert response.status_code == 404

    def test_post__batch__upload_new_file__response_status_200(self, client):
        batch_id_response = client.post("/api/document/v1/documents/multi-upload-session")
        data = {
            "runPipeline": False,
            "batchId": batch_id_response.json()["batchId"],
        }
        files = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
        }
        response = client.post("/api/document/v1/documents/document-file", data=data, files=files)

        assert response.status_code == 200

    def test_post__eml_file__response_status_200(self, client):
        data = {
            "file": ("file.eml", BytesIO(self.make_email_message()), "application/eml"),
        }
        response = client.post("/api/document/v1/documents/document-file", files=data)

        response_json = response.json()

        assert response.status_code == 200
        assert "id" in response_json

    @staticmethod
    def make_email_message() -> bytes:
        msg = EmailMessage()
        msg["Subject"] = "Email message subject"
        msg["From"] = "from@email.com"
        msg["To"] = "to@email.com"
        msg["Body"] = "message body"
        msg["Date"] = datetime.now()
        return msg.as_bytes()

    def test_post__assign_reviewer_on_upload__response_status_200(self, client, uow, set_test_user, user_fixture):
        data = {"assignedToMe": True}

        files = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
        }

        response = client.post("/api/document/v1/documents/document-file", data=data, files=files)
        response_json = response.json()
        created_document = uow.document.get(response_json["id"])

        assert response.status_code == 200
        assert created_document.reviewer is not None
        assert created_document.reviewer.id == user_fixture["subject"]

    def test_post__not_assign_reviewer_on_upload__response_status_200(self, client, uow, set_test_user):
        files = {
            "file": ("document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
        }

        response = client.post("/api/document/v1/documents/document-file", files=files)
        response_json = response.json()
        created_document = uow.document.get(response_json["id"])

        assert response.status_code == 200
        assert created_document.reviewer is None
