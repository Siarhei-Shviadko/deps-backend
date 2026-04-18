from dataclasses import dataclass
from typing import Callable, Optional

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.dtos import UseCaseResponseObject
from deps_documents.domain.entities import DocumentEntityPk, ErrorEntity
from deps_documents.domain.exceptions import DocumentNotFoundError
from deps_documents.domain.interfaces import IDocumentUnitOfWork, IUseCase


@dataclass
class RequestObject:
    document_id: DocumentEntityPk
    error_message: Optional[str] = None


@dataclass
class ResponseObject:
    document_id: DocumentEntityPk


class ServiceFailedUseCase(IUseCase[RequestObject, ResponseObject]):
    Request = RequestObject
    Response = ResponseObject

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
            document_entity.error = ErrorEntity(in_state=document_entity.state, description=request_object.error_message or "")
            document_entity.state = DocumentStateEnum.FAILED
            document_entity = uow.document.update(document_entity)
            uow.commit()
        return ResponseObject(document_id=document_entity.pk)
