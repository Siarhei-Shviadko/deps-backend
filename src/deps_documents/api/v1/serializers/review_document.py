from pydantic import BaseModel, ConfigDict, Field, field_validator

from deps_documents.api.models.strict_str import StrictStr

__all__ = ["SerializedDocumentId"]


class SerializedDocumentId(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    document_ids: list[StrictStr] = Field(..., alias="documentIds", min_items=1)

    @field_validator("document_ids")
    @classmethod
    def validate_document_ids(cls, document_ids):  # noqa: N805
        for document_id in document_ids:
            if not document_id.isdigit():
                raise ValueError(f"Document ID '{document_id}' should be a valid positive integer")

            if int(document_id) < 1:
                raise ValueError(f"Document ID '{document_id}' should be greater than or equal to 1")

        return document_ids
