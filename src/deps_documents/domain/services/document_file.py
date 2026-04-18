from deps_object_storage import FileNotFound, ObjectStorage, StorageNotFound

from deps_documents.domain.entities import BlobFile
from deps_documents.domain.exceptions import DocumentFileNotFoundError


class DocumentFileService:
    def __init__(self, blob_service: ObjectStorage):
        self._blob_service = blob_service

    def retrieve_file_content(self, blob_file: BlobFile) -> bytes:
        try:
            return self._blob_service.download(blob_file.blob_name)
        except (FileNotFound, StorageNotFound):
            raise DocumentFileNotFoundError(f"File {blob_file.blob_name} not found")
