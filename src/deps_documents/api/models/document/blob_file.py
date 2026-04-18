from typing import Optional

from dependency_injector.wiring import Provide, inject
from pydantic import BaseModel, ConfigDict, Field, model_validator

from deps_documents.containers import Container
from deps_documents.infrastructure.services import FileUrlService


class BlobFileModel(BaseModel):
    blob_name: str = Field(alias="blobName")
    url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    @model_validator(mode="after")
    def transform_data(self):
        self.url = get_url(self.blob_name)  # noqa: WPS601
        return self


@inject
def get_url(blob_name: str, file_url_service: FileUrlService = Provide[Container.application_services.file_url]):
    return file_url_service.get_external(blob_name)
