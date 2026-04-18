from typing import Dict, List, Optional
from uuid import uuid4

from deps_documents.domain.entities import (
    DocumentEntity,
    DocumentEntityPk,
    DocumentMetadata,
)

__all__ = ["FakeDocumentRepository"]


class FakeDocumentRepository:
    def __init__(self, fake_db: Optional[Dict[str, DocumentEntity]] = None) -> None:
        self.db = {} if fake_db is None else fake_db
        self.metadata = {}

    def add(self, entity: DocumentEntity) -> DocumentEntity:
        entity.pk = DocumentEntityPk(uuid4().hex)
        self.db[entity.pk] = entity
        return entity

    def get(self, pk: str) -> DocumentEntity:
        return self.db[pk]

    def select_for_update(self, pks: list[str]) -> list[DocumentEntity]:
        return [document for pk, document in self.db.items() if pk in pks]

    def find_by_pks(self, document_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        return [d for d in self.db.values() if d.pk in document_pks]

    def update(self, entity: DocumentEntity) -> DocumentEntity:
        self.db[entity.pk] = entity
        return entity

    def upsert_document_metadata(self, document_metadata: DocumentMetadata) -> None:
        self.metadata[document_metadata.document_id] = document_metadata.metadata

    def get_document_metadata(self, document_pk: DocumentEntityPk) -> DocumentMetadata:
        return DocumentMetadata(document_id=document_pk, metadata=self.metadata.get(document_pk, {}))

    def delete(self, document: DocumentEntity) -> bool:
        return bool(self.db.pop(int(document.pk), None) or self.db.pop(document.pk, None))
