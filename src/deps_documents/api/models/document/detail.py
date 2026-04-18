from pydantic import BaseModel, ConfigDict, Field


class ShortDocumentResponseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    pk: str = Field(..., alias="_id")


class ShortDocumentStatusModel(BaseModel):
    status: str
