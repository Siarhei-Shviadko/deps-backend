from pydantic import BaseModel

from deps_documents.api.models.document.list import ListResponseModel
from deps_documents.domain.entities import RelationType


class RelationTypeListResponseModel(ListResponseModel):
    result: list[RelationType]  # noqa: WPS110


class UpdateRelationTypeResponseModel(BaseModel):
    type: RelationType
