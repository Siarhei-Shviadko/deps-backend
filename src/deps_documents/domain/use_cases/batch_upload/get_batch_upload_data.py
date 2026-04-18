from dataclasses import dataclass
from typing import Dict

from deps_documents.domain.dtos import UseCaseResponseObject
from deps_documents.domain.exceptions import BatchIdNotFoundError
from deps_documents.domain.interfaces import IBatchUploadDataRepository, IUseCase


@dataclass
class RequestObject:
    batch_id: str


@dataclass
class ResponseObject:
    batch_upload_data: Dict[str, str]


class GetBatchUploadDataUseCase(IUseCase[RequestObject, ResponseObject]):
    Request = RequestObject

    def __init__(self, batch_upload_data_repository: IBatchUploadDataRepository):
        self._batch_upload_data_repository = batch_upload_data_repository

    def execute(self, request_object: RequestObject) -> UseCaseResponseObject[ResponseObject]:
        try:
            response = self.process_request(request_object)
        except BatchIdNotFoundError as e:
            return UseCaseResponseObject[ResponseObject].build_error(e)

        return UseCaseResponseObject[ResponseObject].build_success(response)

    def process_request(self, request_object: RequestObject) -> ResponseObject:
        batch_upload_data = self._batch_upload_data_repository.get_batch_upload_data(request_object.batch_id)
        return ResponseObject(batch_upload_data=batch_upload_data)
