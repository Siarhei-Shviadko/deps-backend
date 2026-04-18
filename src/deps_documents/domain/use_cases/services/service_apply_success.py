from dataclasses import dataclass

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.dtos import UseCaseResponseObject
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.exceptions import DocumentNotFoundError
from deps_documents.domain.interfaces import IDocumentService, IUseCase


@dataclass
class RequestObject:
    document_id: DocumentEntityPk
    unassign_reviewer: bool = False


@dataclass
class ResponseObject:
    document_id: DocumentEntityPk


class ServiceSucceededUseCase(IUseCase[RequestObject, ResponseObject]):
    Request = RequestObject

    def __init__(
        self,
        document_service: IDocumentService,
    ) -> None:
        self._document_service = document_service

    def execute(self, request_object: RequestObject):
        try:
            response = self.process_request(request_object)
        except DocumentNotFoundError as e:
            return UseCaseResponseObject[ResponseObject].build_error(e)

        return UseCaseResponseObject[ResponseObject].build_success(response)

    def process_request(self, request_object: RequestObject) -> ResponseObject:
        document_entity = self._document_service.get(DocumentEntityPk(str(request_object.document_id)))
        document_entity.update_state(DocumentStateEnum.COMPLETED)

        if request_object.unassign_reviewer:
            document_entity.unassign_reviewer()

        self._document_service.update(document_entity)

        return ResponseObject(document_id=request_object.document_id)
