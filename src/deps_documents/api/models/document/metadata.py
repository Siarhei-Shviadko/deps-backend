from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from deps_documents.domain.entities import DocumentEntityPk


class DocumentMetadataResponseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    document_id: DocumentEntityPk = Field(..., alias="id")
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("document_id", mode="before")
    @classmethod
    def cast_id_to_str(cls, v):  # noqa: N805
        return str(v)
