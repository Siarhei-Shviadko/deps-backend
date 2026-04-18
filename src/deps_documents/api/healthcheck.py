from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status
from fastapi.responses import Response

from deps_documents.api.endpoint_marker import MarkerRoute
from deps_documents.api.endpoint_visibility import Visibility
from deps_documents.containers import Container
from deps_documents.extras.datasource import Database

healthcheck_router = APIRouter(route_class=MarkerRoute)


@healthcheck_router.get("/healthcheck", tags=["Debug"], openapi_extra={"visibility": Visibility.INTERNAL})
@inject
def service_healthcheck(
    datasources: Database = Depends(Provide[Container.datasources.postgres_datasource]),
):
    """check connection to database"""
    try:
        datasources.healthcheck()
    except Exception:
        return Response(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    return Response(status_code=status.HTTP_200_OK)
