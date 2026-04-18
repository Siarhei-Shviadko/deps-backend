from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from deps_documents.domain.constants import DocumentStateEnum


class ErrorModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    description: str = ""
    in_state: Optional[DocumentStateEnum] = Field(None, alias="inState")
