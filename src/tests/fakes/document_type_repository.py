from deps_documents.domain.entities import DocumentTypeEntity
from deps_documents.domain.exceptions import NotFoundError
from deps_documents.domain.interfaces import IDocumentTypeRepository

__all__ = ["FakeDocumentTypeRepository"]


class FakeDocumentTypeRepository(IDocumentTypeRepository):
    def __init__(self) -> None:
        self._db: dict[tuple[str, str], DocumentTypeEntity] = {}

    def find_by_id_for_tenant(self, document_type_id: str, tenant_id: str) -> DocumentTypeEntity:
        document_type = self._db.get((document_type_id, tenant_id))
        if document_type is None:
            raise NotFoundError(f"Document type with id {document_type_id} not found.")

        return document_type

    def save(self, document_type: DocumentTypeEntity) -> None:
        self._db[(document_type.id, document_type.tenant)] = document_type

    def save_all(self, document_types: list[DocumentTypeEntity]) -> None:
        for document_type in document_types:
            self._db[(document_type.id, document_type.tenant)] = document_type

    def delete(self, document_type: DocumentTypeEntity) -> None:
        self._db.pop((document_type.id, document_type.tenant), None)
