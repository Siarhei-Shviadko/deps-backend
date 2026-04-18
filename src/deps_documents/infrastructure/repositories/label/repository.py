from typing import List

from sqlalchemy import insert, join, select
from sqlalchemy.engine import Connection

from deps_documents.domain.dtos import LabelListFilterObject
from deps_documents.domain.entities.label import LabelEntity, LabelEntityPk
from deps_documents.domain.interfaces.repositories import ILabelRepository
from deps_documents.infrastructure.models import (
    label_table,
    organisation_has_label_table,
)

from .mappers import build_dict_from_entity, build_label_entity


class LabelRepository(ILabelRepository):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    @property
    def get_query(self):
        return select([label_table])

    def add(self, label_entity: LabelEntity) -> LabelEntity:
        query = insert(label_table).values(**build_dict_from_entity(label_entity)).returning(label_table)

        label_obj = self._connection.execute(query).fetchone()

        return build_label_entity(label_obj)

    def get_list(self, options: LabelListFilterObject) -> List[LabelEntity]:
        query = self._filter(options)

        labels = self._connection.execute(query)

        return [build_label_entity(label_entity) for label_entity in labels]

    def add_label_to_organisation(self, label_entity_pk: LabelEntityPk, organisation_name: str) -> None:
        insert_query = insert(organisation_has_label_table).values(
            label_id=label_entity_pk,
            organisation_name=organisation_name,
        )

        self._connection.execute(insert_query)

    def get_organisation_label_entity_pks(
        self,
        organisation_name: str,
        options: LabelListFilterObject,
    ) -> List[LabelEntityPk]:
        joined_tables = join(
            organisation_has_label_table,
            label_table,
            organisation_has_label_table.c.label_id == label_table.c.id,
            isouter=True,
        )
        get_query = (
            select([organisation_has_label_table.c.label_id])
            .select_from(joined_tables)
            .where(organisation_has_label_table.c.organisation_name == organisation_name)
        )
        query = self._filter(options, get_query)

        labels = self._connection.execute(query).fetchall()

        return [LabelEntityPk(str(label[0])) for label in labels]

    def _filter(self, options: LabelListFilterObject, query=None):
        query = query if query is not None else self.get_query

        if options.pks is not None:
            query = query.where(label_table.c.id.in_(options.pks))

        if options.name is not None:
            query = query.where(label_table.c.name == options.name)

        return query
