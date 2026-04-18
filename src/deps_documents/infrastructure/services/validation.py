from json import JSONDecodeError

from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.exceptions import ServiceProxyError
from deps_documents.domain.interfaces.services import IValidationService
from deps_documents.extras.drivers_api import AuthDriverMixin


class ValidationService(AuthDriverMixin, IValidationService):
    def __init__(self, api_host: str) -> None:
        self._url = f"{api_host}/api/validation/v1/document-validation"
        super().__init__()

    def send_document_to_validation(
        self,
        document_id: DocumentEntityPk,
    ) -> None:
        request_data = {"documentPk": document_id}
        response = self._session.post(self._url, params=request_data)
        self._handle_response(response)

    @staticmethod
    def _handle_response(response):
        if not response.ok:
            try:
                message = response.json().get("message", "")
            except JSONDecodeError:
                message = response.text
            finally:
                raise ServiceProxyError(
                    status_code=response.status_code,
                    message=message,
                    service_name="validation",
                )
