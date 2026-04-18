from io import BytesIO
from unittest.mock import MagicMock, patch

from starlette.responses import StreamingResponse

from deps_documents.api.v1.documents import files
from tests.factories import BlobFileFactory, DocumentEntityFactory


class TestDocumentFilesIntegrity:
    REPLACE_FILE_CONTENT_IF_EXISTS = True

    def test_execute__one_file_in_document__return_200(self, client, uow, services):
        document_id = "1"
        document_name = "document_name"

        file_name = "file_name"
        file = BytesIO(b"a new document file content").read()
        blob_name = services.object_storage().upload(file_name, file, replace_if_exists=self.REPLACE_FILE_CONTENT_IF_EXISTS)

        document_entity = DocumentEntityFactory(
            pk=document_id,
            title=document_name,
            files=[BlobFileFactory(blob_name=blob_name)],
        )
        document = uow.document.add(document_entity)

        response = client.get(f"/api/document/v1/documents/{document.pk}/files")

        assert response.status_code == 200

    def test_execute__more_than_one_file_in_document__return_200(self, client, uow, services):
        document_id = "1"
        document_name = "document_name"

        file_name1 = "file_name1"
        file1 = BytesIO(b"a new document file content").read()
        blob_name1 = services.object_storage().upload(file_name1, file1, replace_if_exists=self.REPLACE_FILE_CONTENT_IF_EXISTS)
        file_name2 = "file_name2"
        file2 = BytesIO(b"a new document file content").read()
        blob_name2 = services.object_storage().upload(file_name2, file2, replace_if_exists=self.REPLACE_FILE_CONTENT_IF_EXISTS)

        document_entity = DocumentEntityFactory(
            pk=document_id,
            title=document_name,
            files=[
                BlobFileFactory(blob_name=blob_name1),
                BlobFileFactory(blob_name=blob_name2),
            ],
        )
        uow.document.add(document_entity)

        response = client.get(f"/api/document/v1/documents/{document_id}/files")

        assert response.status_code == 200

    def test_execute__not_exiting_document_id__return_error(self, client):
        response = client.get("/api/document/v1/documents/1/files")

        assert response.status_code == 404
