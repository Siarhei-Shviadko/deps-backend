from sqlalchemy import and_, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from deps_documents.domain.entities import DocumentTypeEntity
from deps_documents.domain.exceptions import NotFoundError
from deps_documents.domain.interfaces import IDocumentTypeRepository
from deps_documents.infrastructure.models import document_type_table

from .mappers import DocumentTypeMapper


class DocumentTypeRepository(IDocumentTypeRepository):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def find_by_id_for_tenant(self, document_type_id: str, tenant_id: str) -> DocumentTypeEntity:
        query = select([document_type_table]).where(
            and_(
                document_type_table.c.id == document_type_id,
                document_type_table.c.tenant == tenant_id,
            ),
        )

        row = self._connection.execute(query).fetchone()
        if not row:
            raise NotFoundError(f"Document type with id {document_type_id} not found.")

        return DocumentTypeMapper.from_dict(row)

    def save(self, document_type: DocumentTypeEntity) -> None:
        raw_document_type = DocumentTypeMapper.to_dict(document_type)

        insert_query = insert(document_type_table).values(**raw_document_type)
        save_query = insert_query.on_conflict_do_update(
            constraint=document_type_table.primary_key,
            set_=dict(insert_query.excluded),
        )

        self._connection.execute(save_query)

    def save_all(self, document_types: list[DocumentTypeEntity]) -> None:
        if not document_types:
            return
        raw_document_types = [DocumentTypeMapper.to_dict(doc_type) for doc_type in document_types]

        insert_query = insert(document_type_table).values(raw_document_types)
        save_query = insert_query.on_conflict_do_update(
            constraint=document_type_table.primary_key,
            set_=dict(insert_query.excluded),
        )

        self._connection.execute(save_query)

    def delete(self, document_type: DocumentTypeEntity) -> None:
        query = delete(document_type_table).where(
            and_(
                document_type_table.c.id == document_type.id,
                document_type_table.c.tenant == document_type.tenant,
            ),
        )
        self._connection.execute(query)
