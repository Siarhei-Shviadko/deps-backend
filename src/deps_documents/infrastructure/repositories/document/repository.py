# flake8: noqa WPS203
from collections import defaultdict
from operator import attrgetter, contains, itemgetter
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import (
    DateTime,
    Text,
    and_,
    bindparam,
    cast,
    delete,
    desc,
    func,
    insert,
    join,
    literal_column,
    not_,
    or_,
    select,
    update,
)
from sqlalchemy.engine import Connection, RowProxy
from sqlalchemy.exc import DatabaseError
from sqlalchemy.sql import Select
from sqlalchemy.sql.functions import count

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.dtos import (
    DocumentListFilterObject,
    PerPageOptions,
    SortingFieldsEnum,
)
from deps_documents.domain.entities import (
    CommunicationEntity,
    DocumentEntity,
    DocumentEntityPk,
    DocumentMetadata,
    GroupEntity,
    LabelEntity,
    LabelEntityPk,
    RelationEntity,
    Reviewer,
)
from deps_documents.domain.exceptions import (
    DocumentAlreadyExistsError,
    DocumentMetadataNotFoundError,
    DocumentNotFoundError,
    LabelForDocumentAlreadyExistsError,
    LabelForDocumentNotFoundError,
    LabelNotFoundError,
    NotFoundError,
    ReviewerNotFoundError,
)
from deps_documents.domain.interfaces import IDocumentEntityRepository
from deps_documents.infrastructure.models import (
    comment_table,
    document_metadata_table,
    document_relation_through_table,
    document_table,
    document_type_table,
    group_table,
    label_table,
    labels_table,
    reviewer_table,
)
from deps_documents.infrastructure.models.document import (
    organisation_has_document_table,
    user_has_document_table,
)
from deps_documents.infrastructure.models.source import source_table
from deps_documents.infrastructure.repositories.error_extractor import (
    extract_database_error_context,
)
from deps_documents.infrastructure.repositories.helpers import (
    batch_pk_validate,
    cast_from_db_pk,
    cast_to_db_pk,
    escape_special_chars,
)

from ..comment.mappers import build_comment_entity
from ..constants import DBErrorTypeEnum
from ..group.mapper import GroupMapper
from ..label.mappers import convert_row_proxy_to_label_entity
from .mappers import (
    build_dict_from_document_metadata_entity,
    build_dict_from_entity,
    build_dict_from_reviewer_entity,
    build_document_entity,
    build_document_metadata_from_db,
    build_reviewer_entity,
    convert_dict_to_document_main_info,
)


class DocumentEntityRepository(IDocumentEntityRepository):  # noqa: WPS214
    @property
    def get_query(self):
        doc = document_table.alias("doc")
        self_left_join = join(document_table, doc, document_table.c.id == doc.c.parent_id, isouter=True)
        return (
            select([document_table, count(doc.c.id).label("first_level_child_count")])
            .select_from(self_left_join)
            .group_by(document_table.c.id)
        )

    @property
    def main_document_columns(self) -> list:
        return [
            document_table.c.id,
            document_table.c.title,
            document_table.c.document_type,
            document_table.c.engine,
            document_table.c.language,
            document_table.c.llm_type,
            document_table.c.state,
            document_table.c.files,
            document_table.c.error_in_state,
        ]

    def __init__(self, connection: Connection):
        self._connection = connection

    def get(self, pk: DocumentEntityPk) -> DocumentEntity:
        obj_query = self.get_query.where(document_table.c.id == cast_to_db_pk(pk))

        doc_in_db = self._connection.execute(obj_query).fetchone()

        if doc_in_db is None:
            raise DocumentNotFoundError(f"Document `{pk}` not found.")

        return self.build_document_entity(doc_in_db)

    def find_by_pks(self, document_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        """
        Get list of DocumentEntities by ids
        """
        valid_document_pks = batch_pk_validate(document_pks)
        documents_query = self.get_query.where(document_table.c.id.in_(valid_document_pks))

        documents = self._connection.execute(documents_query).fetchall()

        no_documents_pks = list(set(valid_document_pks).difference([document["id"] for document in documents]))

        if no_documents_pks:
            raise DocumentNotFoundError(f"Documents with the following key(s) `{no_documents_pks}` not found.")

        return self.build_document_entities(documents)

    def get_main_info_by_pks(self, document_pks: list[DocumentEntityPk]) -> list[dict]:
        valid_document_pks = batch_pk_validate(document_pks)
        documents_query = (
            select([*self.main_document_columns, document_metadata_table.c.metadata])
            .select_from(
                document_table.outerjoin(document_metadata_table, document_metadata_table.c.document_id == document_table.c.id)
            )
            .where(document_table.c.id.in_(valid_document_pks))
        )
        documents = self._connection.execute(documents_query).fetchall()

        no_documents_pks = list(set(valid_document_pks).difference([document["id"] for document in documents]))

        if no_documents_pks:
            raise DocumentNotFoundError(f"Documents with the following key(s) `{no_documents_pks}` not found.")

        return [convert_dict_to_document_main_info(document) for document in documents]

    def add(self, entity: DocumentEntity) -> DocumentEntity:
        doc_dict = build_dict_from_entity(entity)
        insert_query = insert(document_table).values(**doc_dict).returning(literal_column("*"))

        if entity.reviewer and not self._reviewer_exists(entity.reviewer.id):
            self._save_reviewer(entity.reviewer)

        try:
            doc_in_id = self._connection.execute(insert_query).fetchone()
        except DatabaseError as err:
            error_context = extract_database_error_context(err, self._connection.dialect.driver)
            if error_context.error_type == DBErrorTypeEnum.UNIQUE_VIOLATION:
                raise DocumentAlreadyExistsError(f"Document `{entity.pk}` already exists.")
            raise

        return self.build_document_entity(doc_in_id)

    def delete(self, entity: DocumentEntity) -> bool:
        pk = cast_to_db_pk(entity.pk)

        delete_doc_query = delete(document_table).where(document_table.c.id == pk).returning(document_table.c.id)

        deleted_id = self._connection.execute(delete_doc_query).fetchone()

        if deleted_id is None:
            return False

        return True

    def update(self, entity: DocumentEntity) -> DocumentEntity:
        doc_query = select([document_table.c.id]).where(document_table.c.id == cast_to_db_pk(entity.pk))

        updated_fields = self._create_updated_document_entity_dict(entity)

        query = update(document_table).where(document_table.c.id == cast_to_db_pk(entity.pk)).values(**updated_fields)

        if entity.reviewer and not self._reviewer_exists(entity.reviewer.id):
            self._save_reviewer(entity.reviewer)

        doc = self._connection.execute(doc_query).fetchone()

        if doc is None:
            raise DocumentNotFoundError

        self._connection.execute(query)

        return self.get(entity.pk)

    def batch_update(self, document_entities: List[DocumentEntity]) -> List[DocumentEntity]:
        if not document_entities:
            return []
        updated_data = []
        for doc in document_entities:
            doc_update_dict = self._create_updated_document_entity_dict(doc)
            doc_update_dict["pk"] = cast_to_db_pk(doc.pk)
            updated_data.append(doc_update_dict)
            if doc.reviewer and not self._reviewer_exists(doc.reviewer.id):
                self._save_reviewer(doc.reviewer)

        bindparam_update_field = {
            updated_field_name: bindparam(updated_field_name)
            for doc in updated_data
            for updated_field_name in doc
            if updated_field_name != "pk"
        }

        query = update(document_table).where(document_table.c.id == bindparam("pk")).values(bindparam_update_field)

        self._connection.execute(query, updated_data)
        return self.find_by_pks([doc.pk for doc in document_entities])

    def get_list_by_filter(self, filtering: DocumentListFilterObject) -> List[DocumentEntity]:
        query = self._filter(filtering)
        query = self._sort(filtering, query)
        if filtering.per_page is not PerPageOptions.FETCH_ALL_DOCS:
            query = query.offset((filtering.page - 1) * filtering.per_page).limit(filtering.per_page)

        documents = self._connection.execute(query).fetchall()

        return self.build_document_entities(documents)

    def get_total_count_by_filter(self, filtering: DocumentListFilterObject) -> int:
        query_filter = self._filter(filtering)

        result = self._connection.execute(query_filter.alias().count()).fetchone()

        if result is None:
            return 0

        return result[0]

    @staticmethod
    def search(query: str, documents_ids: Optional[List[DocumentEntityPk]] = None):
        query = escape_special_chars(query.lower())

        states = {
            "new": "new",
            "ready": "completed",
            "postponed": "failed",
            "data extraction": "dataextraction",
            "in review": "inreview",
            "preprocessing": "preprocessing",
            "identification": "identification",
        }

        states_for_query = [state_back for state_front, state_back in states.items() if query in state_front]

        joined_tables = (
            document_table.join(labels_table, document_table.c.id == labels_table.c.document_id, isouter=True)
            .join(label_table, labels_table.c.label_id == label_table.c.id, isouter=True)
            .join(
                source_table,
                document_table.c.source_code == source_table.c.code,
                isouter=True,
            )
        )

        columns = func.lower(
            func.concat(
                document_table.c.engine,
                document_table.c.title,
                label_table.c.name,
                source_table.c.title,
                separator=" ",
            )
        )

        where = or_(columns.like(f"%{query}%"), func.lower(document_table.c.state).in_(states_for_query))
        if documents_ids is not None:
            where = and_(where, document_table.c.id.in_(documents_ids))

        return select([document_table]).select_from(joined_tables).where(where).distinct()

    def _filter(self, filtering: DocumentListFilterObject, query=None):  # pylint: disable=too-many-branches
        if filtering.search:
            return self.search(filtering.search, filtering.ids)

        query = query if query is not None else self.get_query
        if filtering.parent_id == "null":
            query = query.where(document_table.c.parent_id.is_(None))
        elif filtering.parent_id:
            query = query.where(document_table.c.parent_id == cast_to_db_pk(filtering.parent_id))

        if filtering.ids is not None:
            query = query.where(document_table.c.id.in_(filtering.ids))
        if filtering.filter_ids is not None:
            query = query.where(document_table.c.id.in_(filtering.filter_ids))

        if filtering.title:
            title = escape_special_chars(filtering.title.lower())
            query = query.where(func.lower(document_table.c.title).like(f"%{title}%"))

        if filtering.reviewer:
            query = query.where(document_table.c.reviewer == filtering.reviewer)

        if filtering.engine:
            query = query.where(document_table.c.engine.in_(filtering.engine))

        if filtering.has_reviewer is not None:
            if filtering.has_reviewer:
                query = query.where(document_table.c.reviewer.isnot(None))
            else:
                query = query.where(document_table.c.reviewer.is_(None))

        if filtering.source:
            query = query.where(document_table.c.source_code.in_(filtering.source))

        if filtering.state:
            query = query.where(document_table.c.state.in_(map(lambda x: x.value, filtering.state)))

        if filtering.document_type:
            query = query.where(document_table.c.document_type.in_(filtering.document_type))

        if filtering.except_types:
            query = query.where(not_(document_table.c.document_type.in_(filtering.except_types)))

        if filtering.labels:
            joined_tables = join(labels_table, label_table, labels_table.c.label_id == label_table.c.id, isouter=True)

            stmt = select([labels_table.c.document_id]).select_from(joined_tables).where(label_table.c.name.in_(filtering.labels))
            query = query.where(document_table.c.id.in_(stmt))

        if filtering.groups:
            query = query.where(document_table.c.group_id.in_(filtering.groups))

        if filtering.datetime_range:
            if filtering.datetime_range.start:
                query = query.where(document_table.c.date.cast(DateTime) >= filtering.datetime_range.start)
            if filtering.datetime_range.end:
                query = query.where(document_table.c.date.cast(DateTime) < filtering.datetime_range.end)
        return query

    def _sort(self, filtering: DocumentListFilterObject, query=None):
        if query is None:
            query = self.get_query

        sort_options = {
            SortingFieldsEnum.pk: document_table.c.id,
            SortingFieldsEnum.title: document_table.c.title,
            SortingFieldsEnum.state: document_table.c.state,
            SortingFieldsEnum.date: document_table.c.date,
            SortingFieldsEnum.source: document_table.c.source_code,
            SortingFieldsEnum.reviewer: document_table.c.reviewer,
            SortingFieldsEnum.engine: document_table.c.engine,
            SortingFieldsEnum.group: document_table.c.group_id,
            SortingFieldsEnum.document_type: document_type_table.c.name,
        }

        if sort_field := filtering.sort_field:
            sort_query = sort_options.get(sort_field)

            if sort_field == SortingFieldsEnum.document_type:
                query = self.join_document_with_document_type(query)

            if filtering.sort_direct:
                sort_query = desc(sort_query)

            query = query.order_by(sort_query)

        return query

    def clear_error(self, pk: DocumentEntityPk) -> bool:
        query = (
            update(document_table)
            .where(document_table.c.id == cast_to_db_pk(pk))
            .values(error_in_state=None, error_description=None)
            .returning(document_table.c.id)
        )

        resp = self._connection.execute(query).fetchone()

        return bool(resp)

    def update_state(self, pk: DocumentEntityPk, state: DocumentStateEnum) -> bool:
        query = (
            update(document_table)
            .where(document_table.c.id == cast_to_db_pk(pk))
            .values(state=cast(state.value, Text))
            .returning(document_table.c.id)
        )

        resp = self._connection.execute(query).fetchone()

        return bool(resp)

    # TODO: rewrite this method
    def add_label(self, label_pk: LabelEntityPk, document_pks: List[DocumentEntityPk]) -> List[DocumentEntityPk]:
        label_query = select([label_table]).where(label_table.c.id == label_pk)

        label_result = self._connection.execute(label_query).fetchone()

        if label_result is None:
            raise LabelNotFoundError(f"Label with pk `{label_pk}` not found.")

        valid_document_pks = batch_pk_validate(document_pks)

        doc_query = select([document_table.c.id]).where(document_table.c.id.in_(valid_document_pks))
        labeled_doc_query = select([labels_table.c.document_id]).where(labels_table.c.label_id == label_result.id)

        doc_ids = list([doc["id"] for doc in self._connection.execute(doc_query).fetchall()])
        labeled_doc_ids = list([doc["document_id"] for doc in self._connection.execute(labeled_doc_query).fetchall()])

        updated_doc_ids = list(set(doc_ids) - set(labeled_doc_ids))

        if updated_doc_ids:
            qr = insert(labels_table).values([{"label_id": label_result.id, "document_id": doc_id} for doc_id in updated_doc_ids])
            self._connection.execute(qr)

        return [cast_from_db_pk(doc_id) for doc_id in updated_doc_ids]

    # TODO: rewrite this method
    def remove_label(self, label_pk: LabelEntityPk, pk: DocumentEntityPk) -> bool:
        label_query = select([label_table]).where(label_table.c.id == label_pk)

        label_result = self._connection.execute(label_query).fetchone()

        if label_result is None:
            raise LabelNotFoundError(f"Label with pk `{label_pk}` not found.")

        doc_query = select([document_table.c.id]).where(document_table.c.id == cast_to_db_pk(pk))

        document = self._connection.execute(doc_query).fetchone()

        if document is None:
            raise DocumentNotFoundError

        labeled_document = select([labels_table]).where(
            and_(labels_table.c.label_id == label_result.id, labels_table.c.document_id == document.id)
        )

        result = self._connection.execute(labeled_document).fetchone()

        if result is None:
            raise LabelForDocumentNotFoundError

        self._connection.execute(
            delete(labels_table).where(
                and_(labels_table.c.label_id == label_result.id, labels_table.c.document_id == document.id)
            )
        )

        return True

    def add_bulk_labels(self, label_pks: list[LabelEntityPk], document_pk: DocumentEntityPk) -> list[LabelEntityPk]:
        doc_id = cast_to_db_pk(document_pk)
        data = [{"label_id": cast_to_db_pk(label_id), "document_id": doc_id} for label_id in label_pks]
        try:
            insert_stmt = insert(labels_table)
            self._connection.execute(insert_stmt, data)
        except DatabaseError as err:
            error_context = extract_database_error_context(err, self._connection.dialect.driver)
            if error_context.error_type == DBErrorTypeEnum.UNIQUE_VIOLATION:
                raise LabelForDocumentAlreadyExistsError(f"Labels for document `{document_pk}` already exists.")
            elif error_context.error_type == DBErrorTypeEnum.FOREIGN_KEY_VIOLATION:
                raise LabelNotFoundError(f"Labels with PKs `{label_pks}` not found.")
            raise

        return label_pks

    def get_document_metadata(self, document_pk: DocumentEntityPk) -> DocumentMetadata:
        select_query = select([document_metadata_table]).where(
            document_metadata_table.c.document_id == cast_to_db_pk(document_pk)
        )

        metadata_db = self._connection.execute(select_query).fetchone()
        if metadata_db is None:
            raise DocumentMetadataNotFoundError(f"Metadata for document `{document_pk}` not found.")

        return build_document_metadata_from_db(metadata_db)

    def upsert_document_metadata(self, document_metadata: DocumentMetadata) -> DocumentMetadata:
        self.delete_document_metadata(document_metadata)

        metadata_db = build_dict_from_document_metadata_entity(document_metadata)
        insert_query = insert(document_metadata_table).values(**metadata_db).returning(literal_column("*"))

        try:
            inserted_metadata = self._connection.execute(insert_query).fetchone()
        except DatabaseError as err:
            error_context = extract_database_error_context(err, self._connection.dialect.driver)
            if error_context.error_type == DBErrorTypeEnum.FOREIGN_KEY_VIOLATION:
                raise DocumentNotFoundError(f"Document `{document_metadata.document_id}` not found, failed to add metadata")
            raise

        return build_document_metadata_from_db(inserted_metadata)

    def delete_document_metadata(self, document_metadata: DocumentMetadata) -> None:
        delete_query = delete(document_metadata_table).where(
            document_metadata_table.c.document_id == document_metadata.document_id
        )
        self._connection.execute(delete_query)

    def get_document_count_of_type(self, document_type_code: str) -> int:
        query = select([func.count()]).select_from(document_table).where(document_table.c.document_type == document_type_code)

        result = self._connection.execute(query).scalar()

        return result

    def find_by_document_type_code(self, document_type_code: str) -> List[DocumentEntity]:
        query = self.get_query.where(document_table.c.document_type == document_type_code)

        documents = self._connection.execute(query).fetchall()

        return self.build_document_entities(documents)

    # TODO: rewrite this method
    def get_descendants(self, pk: DocumentEntityPk, include_containers: bool = False) -> List[DocumentEntity]:
        def bfs(parent_docs: List[RowProxy], accumulator: Tuple[RowProxy, ...]):
            query = select([document_table]).where(document_table.c.parent_id.in_(map(attrgetter("id"), parent_docs)))

            child_documents = self._connection.execute(query).fetchall()

            if child_documents:
                accumulator = accumulator + child_documents
                return bfs(child_documents, accumulator)
            return accumulator

        query = select([document_table]).where(document_table.c.parent_id == pk)

        child_documents = self._connection.execute(query).fetchall()

        all_child_document = bfs(child_documents, child_documents)
        if include_containers is False:
            # Filter only documents without childs
            parent_docs = set(map(attrgetter("parent_id"), all_child_document))
            all_child_document = list(filter(lambda x: not contains(parent_docs, attrgetter("id")(x)), all_child_document))

        return self.build_document_entities(all_child_document)

    def build_document_entity(self, document_row: RowProxy) -> DocumentEntity:
        document_pk = cast_from_db_pk(document_row["id"])
        labels = self.get_assigned_labels(document_pk)
        communication = self.get_assigned_communication(document_pk)
        relation = self.get_assigned_relation(document_pk)
        reviewer = self._find_reviewer(document_row["reviewer"]) if document_row["reviewer"] else None
        group = self._find_group(group_id=document_row["group_id"]) if document_row["group_id"] else None

        return build_document_entity(
            doc_in_db=document_row,
            labels=labels,
            communication=communication,
            assigned_relations=relation,
            reviewer=reviewer,
            group=group,
        )

    def build_document_entities(self, documents_rows: List[RowProxy]) -> List[DocumentEntity]:
        document_pks = [cast_from_db_pk(document_row["id"]) for document_row in documents_rows]
        document_to_labels_mapping = self.get_document_to_labels_mapping(document_pks)
        document_to_communication_mapping = self.get_document_to_communication_mapping(document_pks)
        return [
            build_document_entity(
                document,
                document_to_labels_mapping[cast_from_db_pk(document["id"])],
                document_to_communication_mapping[cast_from_db_pk(document["id"])],
                reviewer=self._find_reviewer(document["reviewer"]) if document["reviewer"] else None,
                group=self._find_group(group_id=document["group_id"]) if document["group_id"] else None,
            )
            for document in documents_rows
        ]

    def get_assigned_labels(self, document_pk: DocumentEntityPk) -> List[LabelEntity]:
        return self.get_document_to_labels_mapping([document_pk])[document_pk]

    def get_assigned_communication(self, document_pk: DocumentEntityPk) -> CommunicationEntity:
        return self.get_document_to_communication_mapping([document_pk])[document_pk]

    def get_document_to_labels_mapping(self, document_pks: List[DocumentEntityPk]) -> Dict[DocumentEntityPk, List[LabelEntity]]:
        joined_tables = join(labels_table, label_table, labels_table.c.label_id == label_table.c.id, isouter=True)

        query = (
            select([labels_table, label_table.c.name.label("label_name")])
            .select_from(joined_tables)
            .where(labels_table.c.document_id.in_(document_pks))
        )

        label_rows = self._connection.execute(query).fetchall()

        document_to_labels_mapping: Dict[DocumentEntityPk, List[LabelEntity]] = defaultdict(list)

        for label_row in label_rows:
            document_to_labels_mapping[cast_from_db_pk(label_row["document_id"])].append(
                convert_row_proxy_to_label_entity(label_row)
            )

        return document_to_labels_mapping

    def check_documents_for_organisation(
        self,
        organisation_entity_name: str,
        document_ids: list[DocumentEntityPk],
    ) -> bool:
        converted_ids = [cast_to_db_pk(doc_id) for doc_id in document_ids]
        query = select([organisation_has_document_table.c.document_id]).where(
            and_(
                organisation_has_document_table.c.document_id.in_(converted_ids),
                organisation_has_document_table.c.organisation_name == organisation_entity_name,
            ),
        )

        documents = self._connection.execute(query).fetchall()

        return len(documents) == len(document_ids)

    def get_document_to_communication_mapping(
        self, document_pks: List[DocumentEntityPk]
    ) -> Dict[DocumentEntityPk, CommunicationEntity]:
        comment_query = select([comment_table]).where(comment_table.c.document_id.in_(document_pks))

        comment_list = self._connection.execute(comment_query).fetchall()

        document_to_communication_mapping: Dict[DocumentEntityPk, CommunicationEntity] = defaultdict(CommunicationEntity)

        for com in comment_list:
            comment = build_comment_entity(com)
            document_to_communication_mapping[cast_from_db_pk(com["document_id"])].comments.append(comment)

        return document_to_communication_mapping

    def get_assigned_relation(self, pk: DocumentEntityPk) -> List[RelationEntity]:
        relation_query = select(
            [document_relation_through_table.c.relation_type, document_relation_through_table.c.relation_code]
        ).where(document_relation_through_table.c.document_id == pk)

        relation_list = self._connection.execute(relation_query)

        return [RelationEntity(type=relation.relation_type, code=relation.relation_code) for relation in relation_list]

    def join_document_with_document_type(self, query) -> Select:
        document = query.froms[0]
        joined = document.join(
            document_type_table,
            document_table.c.document_type == document_type_table.c.id,
            isouter=True,
        )

        query = query.select_from(joined)
        query = query.group_by(document_table.c.id, document_type_table.c.name)

        return query

    def _find_reviewer(self, reviewer_id: str) -> Reviewer:
        reviewer_query = select([reviewer_table]).where(reviewer_table.c.id == reviewer_id)
        reviewer = self._connection.execute(reviewer_query).fetchone()

        if not reviewer:
            raise ReviewerNotFoundError(f"Reviewer {reviewer_id} not found.")

        return build_reviewer_entity(reviewer)

    def _find_group(self, group_id: str) -> GroupEntity:
        query = select([group_table]).where(group_table.c.id == group_id)

        row = self._connection.execute(query).fetchone()
        if not row:
            raise NotFoundError(f"Group with id {group_id} not found.")

        return GroupMapper.from_dict(row)

    def _save_reviewer(self, reviewer: Reviewer) -> Reviewer:
        reviewer_dict = build_dict_from_reviewer_entity(reviewer)
        query = insert(reviewer_table).values(**reviewer_dict).returning(reviewer_table)

        reviewer = self._connection.execute(query).fetchone()

        return build_reviewer_entity(reviewer)

    def add_document_to_user(self, document_entity_pk: DocumentEntityPk, user_entity_pk: str) -> None:
        insert_query = insert(user_has_document_table).values(document_id=document_entity_pk, user_id=user_entity_pk)
        self._connection.execute(insert_query)

    def get_user_document_entity_pks(self, user_entity_pk: str) -> List[DocumentEntityPk]:
        query = select([user_has_document_table.c.document_id]).where(user_has_document_table.c.user_id == user_entity_pk)

        documents = self._connection.execute(query).fetchall()

        return list(map(cast_from_db_pk, map(itemgetter(0), documents)))

    def add_document_to_user_and_organisation(
        self, document_entity_pk: DocumentEntityPk, user_entity_pk: str, organisation_entity_name: str
    ) -> None:
        insert_organisation_query = insert(organisation_has_document_table).values(
            document_id=document_entity_pk, organisation_name=organisation_entity_name
        )
        self.add_document_to_user(document_entity_pk, user_entity_pk)
        self._connection.execute(insert_organisation_query)

    def get_organisation_document_entity_pks(self, organisation_entity_name: str) -> List[DocumentEntityPk]:
        query = select([organisation_has_document_table.c.document_id]).where(
            organisation_has_document_table.c.organisation_name == organisation_entity_name
        )

        documents = self._connection.execute(query).fetchall()

        return list(map(cast_from_db_pk, map(itemgetter(0), documents)))

    @staticmethod
    def _create_updated_document_entity_dict(document_entity: DocumentEntity) -> Dict[str, Any]:
        updated_data = build_dict_from_entity(document_entity)
        updated_fields = {
            "title": updated_data["title"],
            "state": updated_data["state"],
            "files": updated_data["files"],
            "document_type": updated_data["document_type"],
            "sub_type": updated_data["sub_type"],
            "date": updated_data["date"],
            "source_code": updated_data["source_code"],
            "reviewer": updated_data["reviewer"],
            "language": updated_data["language"],
            "engine": updated_data["engine"],
            "llm_type": updated_data["llm_type"],
            "scraped_api_number": updated_data["scraped_api_number"],
            "preview_documents": updated_data["preview_documents"],
            "processing_documents": updated_data["processing_documents"],
            "error_description": updated_data["error_description"],
            "error_in_state": updated_data["error_in_state"],
            "container_type": updated_data["container_type"],
            "container_metadata": updated_data["container_metadata"],
            "group_id": updated_data["group_id"],
            "processing_parameters": updated_data["processing_parameters"],
        }

        return updated_fields

    def select_for_update(self, document_pks: List[DocumentEntityPk]) -> List[DocumentEntity]:
        document_ids = batch_pk_validate(document_pks)
        query = select([document_table]).where(document_table.c.id.in_(document_ids)).with_for_update(read=True)

        documents_rows = self._connection.execute(query).fetchall()

        no_documents_pks = list(set(document_ids).difference([document_row["id"] for document_row in documents_rows]))

        if no_documents_pks:
            raise DocumentNotFoundError(f"Documents with the following key(s) `{no_documents_pks}` not found.")

        return self.build_document_entities(documents_rows)

    def _reviewer_exists(self, reviewer_id: str) -> bool:
        try:
            self._find_reviewer(reviewer_id)
            return True
        except ReviewerNotFoundError:
            return False
