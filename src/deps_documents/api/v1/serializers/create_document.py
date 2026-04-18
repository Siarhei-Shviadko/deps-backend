from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, Json

__all__ = ["CreateDocumentRequest", "CreateDocumentResponse"]


class CreateDocumentRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    document_name: str = Field(alias="documentName")
    document_type_id: Optional[str] = Field(default=None, alias="documentTypeId")
    engine: Optional[str] = None
    language: Optional[str] = None
    llm_type: Optional[str] = Field(default=None, alias="llmType")
    files: list[str]
    assign_to_me: bool = Field(default=False, alias="assignToMe")
    metadata: Optional[Json] = Field(default=None)


class CreateDocumentResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    document_id: str = Field(alias="documentId")
