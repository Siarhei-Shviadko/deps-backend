from http import HTTPStatus
from json import JSONDecodeError
from typing import Optional

from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.exceptions import ServiceProxyError
from deps_documents.extras.drivers_api import AuthDriverMixin


class CorleoneService(AuthDriverMixin):
    def __init__(self, api_host: str, api_port: str, api_endpoint: str) -> None:
        self._corleone_url = f"http://{api_host}:{api_port}{api_endpoint}"
        super().__init__()

    def send_document_to_extraction(
        self,
        document_id: DocumentEntityPk,
        engine: Optional[str] = None,
        language: Optional[str] = None,
    ) -> None:
        request_data = {"documentId": document_id, "engine": engine, "language": language}
        url = f"{self._corleone_url}/extract"
        response = self._session.post(url, json=request_data)
        if not response.ok:
            try:
                message = response.json().get("message", "")
            except JSONDecodeError:
                message = response.text
            finally:
                raise ServiceProxyError(
                    status_code=response.status_code,
                    message=message,
                    service_name="data_extraction",
                )

    def is_extracted_data_exists(
        self,
        document_id: DocumentEntityPk,
    ) -> bool:
        url = f"{self._corleone_url}/extracted-data/{document_id}"
        response = self._session.get(url)
        if response.status_code == HTTPStatus.OK:
            return True
        elif response.status_code == HTTPStatus.NOT_FOUND:
            return False
        else:
            try:
                message = response.json().get("message", "")
            except JSONDecodeError:
                message = response.text
            finally:
                raise ServiceProxyError(
                    status_code=response.status_code,
                    message=message,
                    service_name="data_extraction",
                )
