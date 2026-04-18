from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deps_documents.domain.entities import DocumentEntityPk


class CommentRequestModel(BaseModel):
    document_id: DocumentEntityPk = Field(..., alias="documentId")
    text: str = Field(...)


class CommentModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    text: str
    created_at: datetime = Field(alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")

    @field_validator("created_at")
    @classmethod
    def datetime_to_string(cls, v):  # noqa: N805
        if v:
            return v.isoformat()


class CommentsListModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    comments: list[CommentModel] = Field(default_factory=list)


class CommentResponseModel(CommentModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
