from pydantic import BaseModel, ConfigDict, Field

from deps_documents.domain.entities import GroupEntity


class SerializedGroupInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    group_id: str = Field(..., alias="groupId")
    group_name: str = Field(..., alias="groupName")

    @classmethod
    def from_domain(cls, group: GroupEntity) -> "SerializedGroupInfo":
        return cls(group_id=group.id, group_name=group.name)

    def to_domain(self) -> GroupEntity:
        return GroupEntity(
            id=self.group_id,
            name=self.group_name,
        )
