from pydantic import BaseModel, ConfigDict


class RelationModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str
    code: str
