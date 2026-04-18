from pydantic import BaseModel, ConfigDict, Field, field_validator


class MultiUploadSessionResponseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    batch_id: str = Field(..., alias="batchId")


class UploadFileResponseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    document_id: str = Field(..., alias="id")
    message: str

    @field_validator("document_id", mode="before")
    @classmethod
    def cast_id_to_str(cls, v):  # noqa: N805
        return str(v)
