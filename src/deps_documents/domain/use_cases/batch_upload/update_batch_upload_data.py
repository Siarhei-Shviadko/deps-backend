from dataclasses import dataclass
from typing import Dict

from deps_documents.domain.dtos import UseCaseResponseObject
from deps_documents.domain.exceptions import BatchIdNotFoundError
from deps_documents.domain.interfaces import IBatchUploadDataRepository, IUseCase


@dataclass
class RequestObject:
    batch_id: str
    batch_upload_data: Dict[str, str]


@dataclass
class ResponseObject:
    status: bool


class UpdateBatchUploadDataUseCase(IUseCase[RequestObject, ResponseObject]):
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
        self._batch_upload_data_repository.update_batch_upload_data(request_object.batch_id, request_object.batch_upload_data)
        return ResponseObject(status=True)
