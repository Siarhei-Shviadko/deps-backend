from dataclasses import dataclass
from typing import Callable

from deps_documents.domain.dtos import UseCaseResponseObject
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.exceptions import (
    DocumentClassificationError,
    DocumentNotFoundError,
)
from deps_documents.domain.interfaces import IDocumentUnitOfWork, IUseCase


@dataclass
class RequestObject:
    document_id: DocumentEntityPk
    document_type: str


@dataclass
class ResponseObject:
    document_id: DocumentEntityPk


class ApplyClassificationResultUseCase(IUseCase[RequestObject, ResponseObject]):
    Request = RequestObject

    def __init__(self, unit_of_work: Callable[..., IDocumentUnitOfWork]) -> None:
        self._uow = unit_of_work

    def execute(self, request_object: RequestObject):
        try:
            response = self.process_request(request_object)
        except DocumentNotFoundError as e:
            return UseCaseResponseObject[ResponseObject].build_error(e)

        return UseCaseResponseObject[ResponseObject].build_success(response)

    def process_request(self, request_object: RequestObject) -> ResponseObject:
        if not request_object.document_type or request_object.document_type == "unknown":
            raise DocumentClassificationError("Failed to classify document")

        with self._uow() as uow:
            document_entity = uow.document.get(request_object.document_id)
            document_entity.document_type = request_object.document_type
            document_entity = uow.document.update(document_entity)
            uow.commit()
        return ResponseObject(document_id=document_entity.pk)
