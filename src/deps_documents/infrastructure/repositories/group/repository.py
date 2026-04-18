from sqlalchemy import and_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.engine import Connection

from deps_documents.domain.dtos import GroupInfo
from deps_documents.domain.entities import GroupEntity
from deps_documents.domain.exceptions import NotFoundError
from deps_documents.domain.interfaces import IGroupRepository
from deps_documents.infrastructure.models import group_table

from .mapper import GroupMapper


class GroupRepository(IGroupRepository):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def find_by_id_for_tenant(self, group_id: str, tenant_id: str) -> GroupEntity:
        query = select([group_table]).where(
            and_(
                group_table.c.id == group_id,
                group_table.c.tenant_id == tenant_id,
                group_table.c.is_deleted.is_(False),
            ),
        )

        row = self._connection.execute(query).fetchone()
        if not row:
            raise NotFoundError(f"Group with id {group_id} not found for tenant {tenant_id}.")

        return GroupMapper.from_dict(row)

    def save(self, group_id: str, tenant_id: str, name: str) -> None:
        insert_query = insert(group_table).values(
            id=group_id,
            tenant_id=tenant_id,
            name=name,
        )
        save_query = insert_query.on_conflict_do_update(
            constraint=group_table.primary_key,
            set_=dict(insert_query.excluded),
        )

        self._connection.execute(save_query)

    def save_all(self, groups: list[GroupInfo]) -> None:
        if not groups:
            return
        insert_query = insert(group_table).values(groups)
        save_query = insert_query.on_conflict_do_update(
            constraint=group_table.primary_key,
            set_=dict(insert_query.excluded),
        )

        self._connection.execute(save_query)

    def mark_deleted(self, group_id: str, tenant_id: str) -> None:
        query = (
            update(group_table)
            .where(
                and_(
                    group_table.c.id == group_id,
                    group_table.c.tenant_id == tenant_id,
                ),
            )
            .values(is_deleted=True)
        )

        self._connection.execute(query)
