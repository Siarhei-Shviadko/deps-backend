from dataclasses import asdict
from typing import List

from sqlalchemy import and_, delete, insert, literal_column, select, update
from sqlalchemy.engine import Connection
from sqlalchemy.exc import DatabaseError

from deps_documents.domain.dtos import RelationFilterObject, UpdateRelationEntity
from deps_documents.domain.entities import RelationEntity, RelationType
from deps_documents.domain.exceptions import (
    AssignedDocumentDeletingError,
    DocumentAlreadyAssignedError,
    DocumentAssigningError,
    RelationAlreadyExistsError,
    RelationChildrenNotFoundError,
    RelationNotFoundError,
    RelationParentNotFoundError,
    RelationTypeAlreadyExistsError,
    RelationTypeNotFoundError,
    RelationTypeUpdatingError,
    RelationUpdatingError,
)
from deps_documents.domain.interfaces import IRelationRepository
from deps_documents.infrastructure.models import (
    document_relation_through_table,
    relation_table,
    relation_type_table,
)
from deps_documents.infrastructure.repositories.constants import DBErrorTypeEnum
from deps_documents.infrastructure.repositories.error_extractor import (
    extract_database_error_context,
)

from .mapper import build_relation_entity


class RelationRepository(IRelationRepository):  # noqa: WPS214
    def __init__(self, connection: Connection):
        self._connection = connection

    def get_relation(
        self,
        relation: RelationEntity,
    ) -> RelationEntity:
        rel_filter = RelationFilterObject(type=relation.type, code=relation.code)
        return self.get_relation_list(rel_filter)[0]

    def get_relation_list(
        self,
        relation_filter: RelationFilterObject = RelationFilterObject(),
    ) -> List[RelationEntity]:
        query = select([relation_table])
        if relation_filter.type is not None:
            query = query.where(relation_table.c.type == relation_filter.type)

        if relation_filter.code is not None:
            query = query.where(relation_table.c.code == relation_filter.code)

        relation_db_obj = self._connection.execute(query)  # noqa: WPS204

        relation_list = [
            build_relation_entity(relation, self.get_assigned_documents(relation=relation)) for relation in relation_db_obj
        ]

        if len(relation_list) == 0:  # noqa: WPS507
            if relation_filter.type is None and relation_filter.code is None:
                return relation_list
            raise RelationNotFoundError(relation_filter)
        return relation_list

    def get_children_list(self, relation: RelationEntity) -> List[RelationEntity]:
        query = select([relation_table]).where(
            and_(relation_table.c.parent_type == relation.type, relation_table.c.parent_code == relation.code),
        )
        relation_db_obj = self._connection.execute(query)  # noqa: WPS204

        relation_list = [build_relation_entity(relation, self.get_assigned_documents(relation)) for relation in relation_db_obj]

        if len(relation_list) == 0:  # noqa: WPS507
            self.get_relation(relation)
            raise RelationChildrenNotFoundError(relation)
        return relation_list

    def get_relation_type_list(self) -> List[RelationType]:
        query = select([relation_type_table])
        db_types = self._connection.execute(query)

        return [db_type.type for db_type in db_types]

    def get_assigned_documents(self, relation: RelationEntity) -> List[int]:
        query = select([document_relation_through_table]).where(
            and_(
                document_relation_through_table.c.relation_type == relation.type,
                document_relation_through_table.c.relation_code == relation.code,
            ),
        )
        assigned_docs = self._connection.execute(query)
        return [doc.document_id for doc in assigned_docs]

    def add(self, relation: RelationEntity) -> RelationEntity:
        return self.create_relation(relation)

    def create_relation(self, relation: RelationEntity) -> RelationEntity:  # noqa: WPS238
        values = asdict(relation)
        values.pop("assigned_documents")

        query = insert(relation_table).values(**values).returning(literal_column("*"))

        fk_exp = {
            "fk_parent_type_code": RelationParentNotFoundError(relation),
            "fk_relation_type": RelationTypeNotFoundError(relation),
        }

        try:
            created_relation = self._connection.execute(query).fetchone()
        except DatabaseError as err:
            error_context = extract_database_error_context(err, self._connection.dialect.driver)
            if error_context.error_type == DBErrorTypeEnum.UNIQUE_VIOLATION:
                raise RelationAlreadyExistsError(relation)
            elif error_context.error_type == DBErrorTypeEnum.FOREIGN_KEY_VIOLATION:
                if error_context.constraint_name in fk_exp:
                    raise fk_exp.get(error_context.constraint_name)  # noqa: WPS220
            raise

        return build_relation_entity(created_relation)

    def create_relation_type(self, relation_type: str) -> None:
        query = insert(relation_type_table).values(type=relation_type)

        try:
            self._connection.execute(query)
        except DatabaseError as err:
            error_context = extract_database_error_context(err, self._connection.dialect.driver)
            if error_context.error_type == DBErrorTypeEnum.UNIQUE_VIOLATION:
                raise RelationTypeAlreadyExistsError(relation_type=relation_type)
            raise

    def assign_document(self, relation: RelationEntity) -> None:  # noqa: WPS238
        relation_docs = [
            {"relation_code": relation.code, "relation_type": relation.type, "document_id": doc_id}
            for doc_id in relation.assigned_documents
        ]
        fk_exp = {
            "fk_relation_type_code": RelationNotFoundError(relation),
            "fk_document": DocumentAssigningError(doc_ids=relation.assigned_documents),
        }

        query = insert(document_relation_through_table).values(relation_docs)

        try:
            self._connection.execute(query)
        except DatabaseError as err:
            error_context = extract_database_error_context(err, self._connection.dialect.driver)
            if error_context.error_type == DBErrorTypeEnum.UNIQUE_VIOLATION:
                raise DocumentAlreadyAssignedError(doc_ids=relation.assigned_documents)
            elif error_context.error_type == DBErrorTypeEnum.FOREIGN_KEY_VIOLATION:
                if error_context.constraint_name in fk_exp:
                    raise fk_exp.get(error_context.constraint_name)  # noqa: WPS220
            raise

    def update(self, relation: RelationEntity, relation_update_info: UpdateRelationEntity) -> RelationEntity:
        values_to_update = {key: value for key, value in asdict(relation_update_info).items() if value is not None}
        values_to_update.pop("assigned_documents")

        query = (
            update(relation_table)
            .where(and_(relation_table.c.code == relation.code, relation_table.c.type == relation.type))
            .values(**values_to_update)
            .returning(literal_column("*"))
        )

        try:
            updated_relation = self._connection.execute(query)
        except DatabaseError as err:
            error_context = extract_database_error_context(err, self._connection.dialect.driver)
            if error_context.error_type == DBErrorTypeEnum.UNIQUE_VIOLATION:
                raise RelationUpdatingError(
                    relation=relation,
                    update_entity=relation_update_info,
                )
            raise
        if updated_relation.rowcount == 0:
            raise RelationNotFoundError(relation)
        updated_relation = updated_relation.fetchone()

        relation_for_assign = build_relation_entity(updated_relation, assigned_documents=relation_update_info.assigned_documents)
        self.assign_document(relation=relation_for_assign)

        relation_for_assign.assigned_documents = self.get_assigned_documents(relation_for_assign)
        return relation_for_assign

    def update_relation_type(self, relation_type: str, type_update_info: RelationType) -> RelationType:
        values_to_update = {"type": type_update_info}
        query = (
            update(relation_type_table)
            .where(relation_type_table.c.type == relation_type)
            .values(**values_to_update)
            .returning(literal_column("type"))
        )

        try:
            updated_type = self._connection.execute(query)
        except DatabaseError as err:
            error_context = extract_database_error_context(err, self._connection.dialect.driver)
            if error_context.error_type == DBErrorTypeEnum.UNIQUE_VIOLATION:
                raise RelationTypeUpdatingError(relation_type=relation_type, new_relation_type=type_update_info)
            raise
        if updated_type.rowcount == 0:
            raise RelationTypeNotFoundError(relation_type=relation_type)
        updated_type = updated_type.fetchone()

        return updated_type.type

    def delete_relation(
        self,
        relation: RelationEntity,
    ) -> bool:
        query = delete(relation_table).where(
            and_(
                relation_table.c.type == relation.type,
                relation_table.c.code == relation.code,
            ),
        )
        delete_status = self._connection.execute(query)

        if delete_status.rowcount == 0:
            raise RelationNotFoundError(relation)

        return True

    def delete_assigned_documents(
        self,
        relation: RelationEntity,
    ) -> bool:
        query = delete(document_relation_through_table).where(
            and_(
                document_relation_through_table.c.relation_code == relation.code,
                document_relation_through_table.c.relation_type == relation.type,
            ),
        )
        if relation.assigned_documents:
            query = query.where(document_relation_through_table.c.document_id.in_(relation.assigned_documents))

        delete_status = self._connection.execute(query)

        if delete_status.rowcount == 0:
            self.get_relation(relation)
            raise AssignedDocumentDeletingError(doc_ids=relation.assigned_documents)

        return True
