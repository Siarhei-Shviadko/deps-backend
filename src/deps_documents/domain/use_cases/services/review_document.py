from dataclasses import dataclass
from typing import Callable

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.dtos import UseCaseResponseObject
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.exceptions import DocumentNotFoundError
from deps_documents.domain.interfaces import IDocumentUnitOfWork, IUseCase


@dataclass
class RequestObject:
    document_id: DocumentEntityPk


@dataclass
class ResponseObject:
    pass  # noqa: WPS420 WPS604


class ReviewUseCase(IUseCase[RequestObject, ResponseObject]):
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
        with self._uow() as uow:
            document_entity = uow.document.get(request_object.document_id)
            document_entity.state = DocumentStateEnum.IN_REVIEW
            uow.document.update(document_entity)
            uow.commit()
        return ResponseObject()
