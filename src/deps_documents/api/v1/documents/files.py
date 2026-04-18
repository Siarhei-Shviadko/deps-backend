import io
import os
import zipfile
from urllib.parse import quote

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.containers import Container
from deps_documents.domain.dtos import DocumentFilesDataObject
from deps_documents.domain.entities import BlobFile, DocumentEntityPk
from deps_documents.domain.interfaces import IDocumentService
from deps_documents.domain.services import DocumentFileService

router = APIRouter(route_class=MarkerRoute)

DEFAULT_CHUNK_SIZE = 8192


def chunk_stream(file: io.BytesIO, chunk_size: int = DEFAULT_CHUNK_SIZE):
    while chunk := file.read(chunk_size):
        yield chunk


@inject
def _generate_file_for_download(  # noqa: WPS210
    document_file_obj: DocumentFilesDataObject,
    document_file_service: DocumentFileService = Provide[Container.domain_services.document_file],
) -> StreamingResponse:
    def _create_zip_file(blob_files: list[str]) -> io.BytesIO:  # noqa: WPS430
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for blob_file in blob_files:
                file_content = document_file_service.retrieve_file_content(blob_file=BlobFile(blob_name=blob_file))
                short_file_name = blob_file.split("/")[-1]
                zip_file.writestr(short_file_name, file_content)
        zip_buffer.seek(0, 0)
        return zip_buffer

    file_name_no_ext, _ = os.path.splitext(document_file_obj.document_name)
    quoted_file_name_no_ext = quote(file_name_no_ext)

    if len(document_file_obj.files_names) == 1:
        file_content = document_file_service.retrieve_file_content(
            blob_file=BlobFile(blob_name=document_file_obj.files_names[0]),
        )
        _, file_ext = os.path.splitext(document_file_obj.files_names[0])
        new_file_name = f"{quoted_file_name_no_ext}{file_ext}"
        in_mem_file = io.BytesIO(file_content)
        return StreamingResponse(
            content=chunk_stream(in_mem_file),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'inline; filename="{new_file_name}"'},
        )

    new_file_name = f"{quoted_file_name_no_ext}.zip"
    zip_file = _create_zip_file(document_file_obj.files_names)
    return StreamingResponse(
        content=zip_file,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{new_file_name}"'},
    )


@router.get("/{document_id}/preprocessed-images", openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def download_preprocessed_documents(
    document_id: DocumentEntityPk,
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    preprocesssed_documents = document_service.get_processed_images(document_entity_pk=document_id)
    return _generate_file_for_download(preprocesssed_documents)


@router.get("/{document_id}/files", response_class=StreamingResponse, openapi_extra={"visibility": Visibility.PUBLIC})
@inject
def download_original_documents(
    document_id: DocumentEntityPk,
    document_service: IDocumentService = Depends(Provide[Container.domain_services_accessor.document]),
):
    original_documents = document_service.get_document_files(document_entity_pk=document_id)
    return _generate_file_for_download(original_documents)
