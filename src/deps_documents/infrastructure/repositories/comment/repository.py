from sqlalchemy import insert
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DatabaseError

from deps_documents.domain.entities import CommentEntity, DocumentEntityPk
from deps_documents.domain.exceptions import DocumentNotFoundError
from deps_documents.domain.interfaces import ICommentRepository
from deps_documents.infrastructure.models import comment_table
from deps_documents.infrastructure.repositories.constants import DBErrorTypeEnum
from deps_documents.infrastructure.repositories.error_extractor import (
    extract_database_error_context,
)

from .mappers import build_comment_entity, build_dict_from_comment_entity


class CommentRepository(ICommentRepository):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def add(self, comment_entity: CommentEntity, document_entity_pk: DocumentEntityPk) -> CommentEntity:
        comment_dict = build_dict_from_comment_entity(comment_entity)
        comment_dict["document_id"] = document_entity_pk

        insert_comment_query = insert(comment_table).values(**comment_dict).returning(comment_table)

        try:
            comment_obj = self._connection.execute(insert_comment_query).fetchone()
        except DatabaseError as err:
            error_context = extract_database_error_context(err, self._connection.dialect.driver)
            if error_context.error_type == DBErrorTypeEnum.FOREIGN_KEY_VIOLATION:
                raise DocumentNotFoundError(f"Document `{document_entity_pk}` not found.")
            raise

        return build_comment_entity(comment_obj)
