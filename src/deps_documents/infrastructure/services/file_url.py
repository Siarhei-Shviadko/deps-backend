from deps_documents.domain.interfaces import IFileUrlService


class FileUrlService(IFileUrlService):
    def __init__(self, file_service_external_url, file_service_internal_url):
        self._file_service_external_url = file_service_external_url
        self._file_service_internal_url = file_service_internal_url

    def get_external(self, file_path):
        return "/".join((self._file_service_external_url, file_path)).rstrip("/")

    def get_internal(self, file_path):
        return "/".join((self._file_service_internal_url, file_path)).rstrip("/")
