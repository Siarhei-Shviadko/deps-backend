from typing import Any

from deps_documents.domain.entities import GroupEntity
from deps_documents.domain.exceptions import NotFoundError
from deps_documents.domain.interfaces import IGroupRepository

__all__ = ["FakeGroupRepository"]


class FakeGroupRepository(IGroupRepository):
    def __init__(self) -> None:
        self._db: dict[tuple[str, str], GroupEntity] = {}

    def find_by_id_for_tenant(self, group_id: str, tenant_id: str) -> GroupEntity:
        group = self._db.get((group_id, tenant_id))
        if group is None:
            raise NotFoundError(f"Group with id {group_id} not found for tenant {tenant_id}.")

        return group

    def save(self, group_id: str, tenant_id: str, name: str) -> None:
        self._db[(group_id, tenant_id)] = GroupEntity(id=group_id, name=name)

    def save_all(self, groups: list[dict[str, Any]]) -> None:
        for group in groups:
            self._db[(group["id"], group["tenant_id"])] = GroupEntity(id=group["id"], name=group["name"])

    def mark_deleted(self, group_id: str, tenant_id: str) -> None:
        self._db.pop((group_id, tenant_id), None)
