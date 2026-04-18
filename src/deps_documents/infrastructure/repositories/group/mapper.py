from typing import Any

from deps_documents.domain.entities import GroupEntity


class GroupMapper:
    @staticmethod
    def to_dict(group: GroupEntity) -> dict[str, Any]:
        return {
            "id": group.id,
            "name": group.name,
        }

    @staticmethod
    def from_dict(group: dict[str, Any]) -> GroupEntity:
        return GroupEntity(id=group["id"], name=group["name"])
