from .common import NotFoundError


class DocumentMetadataNotFoundError(NotFoundError):
    code = "document_metadata_not_found"
