from typing import Any

from deps_documents.domain.entities import DocumentTypeEntity


class DocumentTypeMapper:
    @staticmethod
    def to_dict(document_type: DocumentTypeEntity) -> dict[str, Any]:
        return {
            "id": document_type.id,
            "tenant": document_type.tenant,
            "name": document_type.name,
        }

    @staticmethod
    def from_dict(document_type: dict[str, Any]) -> DocumentTypeEntity:
        return DocumentTypeEntity(
            id=document_type["id"],
            tenant=document_type["tenant"],
            name=document_type["name"],
        )
