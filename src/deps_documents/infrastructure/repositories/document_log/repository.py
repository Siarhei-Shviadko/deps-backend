from typing import List

from sqlalchemy import insert, literal_column, select
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DatabaseError

from deps_documents.domain.entities import DocumentEntityPk, DocumentLogEntity
from deps_documents.domain.exceptions import (
    DocumentLogAlreadyExistsError,
    DocumentNotFoundError,
)
from deps_documents.domain.interfaces import IDocumentLogRepository
from deps_documents.infrastructure.models import document_log_table, document_table
from deps_documents.infrastructure.repositories.constants import DBErrorTypeEnum
from deps_documents.infrastructure.repositories.error_extractor import (
    extract_database_error_context,
)
from deps_documents.infrastructure.repositories.helpers import cast_to_db_pk

from .mappers import build_dict_from_entity, build_document_log_entity


class DocumentLogEntityRepository(IDocumentLogRepository):
    def __init__(self, connection: Connection) -> None:
        self._conn = connection

    def add(self, entity: DocumentLogEntity) -> DocumentLogEntity:
        document_id = cast_to_db_pk(entity.document_id)
        query = select([document_table]).where(document_table.c.id == document_id)

        doc_log_in_db = self._conn.execute(query).fetchone()

        if doc_log_in_db is None:
            raise DocumentNotFoundError(f"Document `{document_id}` not found.")

        log_dict = build_dict_from_entity(entity)
        log_query = insert(document_log_table).values(**log_dict).returning(literal_column("*"))

        try:
            log = self._conn.execute(log_query).fetchone()
        except DatabaseError as err:
            error_context = extract_database_error_context(err, self._conn.dialect.driver)
            if error_context.error_type == DBErrorTypeEnum.UNIQUE_VIOLATION:
                raise DocumentLogAlreadyExistsError(f"Document `{entity.pk}` already exists.")
            raise

        return build_document_log_entity(log)

    def get_document_logs(self, document_id: DocumentEntityPk) -> List[DocumentLogEntity]:
        document_id = cast_to_db_pk(document_id)
        query = select([document_table]).where(document_table.c.id == document_id)
        logs_query = select([document_log_table]).where(document_log_table.c.document_id == cast_to_db_pk(document_id))

        doc = self._conn.execute(query).fetchone()

        if doc is None:
            raise DocumentNotFoundError(f"Document `{document_id}` not found.")

        logs = self._conn.execute(logs_query).fetchall()

        return [build_document_log_entity(log) for log in logs]
