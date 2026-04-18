from pydantic import BaseModel, ConfigDict, Field

__all__ = ["BaseSerializer", "CreateDocumentResponse", "CreateDocumentFromFileResponse"]


class BaseSerializer(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class CreateDocumentResponse(BaseSerializer):
    document_id: str = Field(..., alias="id")


class CreateDocumentFromFileResponse(BaseSerializer):
    document_id: str = Field(..., alias="documentId")
    document_name: str = Field(..., alias="documentName")
