from typing import Optional

from deps_documents.domain.entities import DocumentMetadata

__all__ = ["FakeDocumentMetadataRepository"]


class FakeDocumentMetadataRepository:
    def __init__(self, fake_db: Optional[dict[str, dict]] = None) -> None:
        self.db = {} if fake_db is None else fake_db

    def upsert_document_metadata(self, document_metadata: DocumentMetadata) -> DocumentMetadata:
        self.db[document_metadata.document_id] = document_metadata.metadata
        return document_metadata
