import io

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from starlette.responses import StreamingResponse

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.containers import Container
from deps_documents.domain.entities import BlobFile
from deps_documents.domain.services import DocumentFileService

router = APIRouter(prefix="/files", tags=["Document file"], route_class=MarkerRoute)


@router.get("/file-content", openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def get_file_content(
    blob: str = Query(...),
    document_file_service: DocumentFileService = Depends(Provide[Container.domain_services.document_file]),
):
    file_content = document_file_service.retrieve_file_content(blob_file=BlobFile(blob_name=blob))
    in_mem_file = io.BytesIO(file_content)
    return StreamingResponse(
        content=in_mem_file,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'inline; filename="{blob}"'},
    )
