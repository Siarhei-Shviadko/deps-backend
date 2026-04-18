import pytest
from deps_object_storage import FileNotFound

from deps_documents.domain.entities import BlobFile
from deps_documents.domain.exceptions import DocumentFileNotFoundError


@pytest.fixture
def domain_services(domain_services):
    domain_services.document_file.reset_override()

    return domain_services


class TestDocumentFileService:
    def test_retrieve_file_content__existing_file__return_content(self, domain_services, services, blob_storage_mock):
        blob_storage_mock.upload("blob_name", b"Test value", replace_if_exists=True)
        result = domain_services.document_file().retrieve_file_content(BlobFile(blob_name="blob_name"))

        assert result

    def test_retrieve_file_content__not_existing_file__raise_not_found(self, domain_services, services, blob_storage_mock):
        with pytest.raises(DocumentFileNotFoundError):
            domain_services.document_file().retrieve_file_content(BlobFile(blob_name="blob_name"))
