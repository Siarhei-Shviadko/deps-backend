from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LabelModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    pk: Optional[str] = Field(alias="_id")
    name: str = Field(...)
