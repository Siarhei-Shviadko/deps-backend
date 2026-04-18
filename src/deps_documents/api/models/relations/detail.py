from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class RelationResponseModel(BaseModel):
    status: str


class RelationDeleteResponseModel(BaseModel):
    deleted: bool


class RelationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    type: str
    code: str
    metadata: Optional[dict[str, Any]] = None
    assigned_documents: list[int] = Field(default_factory=list, alias="assignedDocuments")
    parent_type: Optional[str] = Field(None, alias="parentType")
    parent_code: Optional[str] = Field(None, alias="parentCode")


class AddRelationResponseModel(BaseModel):
    relation: RelationModel


class RelationPutModel(RelationModel):
    code: Optional[str] = Field(None, min_length=1)
    type: Optional[str] = Field(None, min_length=1)
