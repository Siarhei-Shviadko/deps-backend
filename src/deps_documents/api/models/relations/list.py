from deps_documents.api.models.document.document import DocumentModel
from deps_documents.api.models.document.list import ListResponseModel
from deps_documents.api.models.relations.detail import RelationModel


class ListRelationResponseModel(ListResponseModel):
    result: list[RelationModel]  # noqa: WPS110


class DocumentListRelationResponseModel(ListResponseModel):
    result: list[DocumentModel]  # noqa: WPS110
