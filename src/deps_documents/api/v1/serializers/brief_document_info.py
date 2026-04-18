from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from deps_documents.domain.constants import DocumentStateEnum

__all__ = ["GetBriefDocumentsInfoResponse", "BriefDocumentInfo"]


class BriefDocumentInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    title: str
    state: DocumentStateEnum
    files: list[str]
    type_id: Optional[str] = Field(None, alias="typeId")
    engine: Optional[str] = None
    language: Optional[str] = None
    llm_type: Optional[str] = Field(None, alias="llmType")
    error_in_state: Optional[DocumentStateEnum] = Field(None, alias="errorInState")
    metadata: Optional[dict[str, Any]] = None

    @classmethod
    def from_dict(cls, document: dict) -> "BriefDocumentInfo":
        return cls(
            id=document["pk"],
            title=document["title"],
            type_id=document["type"],
            state=document["state"],
            files=[file.blob_name for file in document["files"]],
            engine=document["engine"],
            language=document["language"],
            llm_type=document["llm_type"],
            error_in_state=document["error_in_state"],
            metadata=document["metadata"],
        )


class GetBriefDocumentsInfoResponse(BaseModel):
    documents: list[BriefDocumentInfo]
