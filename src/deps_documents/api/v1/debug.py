from fastapi import APIRouter
from starlette import status

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility

router = APIRouter(prefix="/debug", tags=["Debug"], route_class=MarkerRoute)


@router.get("/500", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, openapi_extra={"visibility": Visibility.INTERNAL})
def raise_internal_server_error():
    raise ValueError()
