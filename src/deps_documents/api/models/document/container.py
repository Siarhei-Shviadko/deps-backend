from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ContainerMetadataModel(BaseModel):
    first_level_child_count: Optional[int] = Field(1, alias="firstLevelChildCount")


class ContainerEmailMetadataModel(ContainerMetadataModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    subject: Optional[str] = None
    sender: Optional[str] = None
    recipients: Optional[list[str]] = None
    cc: Optional[list[str]] = None
    body: Optional[str] = None
    date: Optional[str] = None
