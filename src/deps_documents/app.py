import logging
from http import HTTPStatus

from fastapi import FastAPI
from fastapi.requests import Request

from deps_documents import api, auth, constants
from deps_documents.api.healthcheck import healthcheck_router
from deps_documents.api.internal import internal_router
from deps_documents.api.service_info import service_info_router
from deps_documents.api.v1 import v1_router
from deps_documents.api.v2 import v2_router
from deps_documents.config import Settings
from deps_documents.containers import Container
from deps_documents.domain.exceptions import AuthError, ForbiddenError
from deps_documents.error_handlers import (
    json_domain_error_handler,
    register_errorhandler,
)
from deps_documents.events_handler import command_handlers, handlers
from deps_documents.extras.fastapi_utils import add_auth_to_openapi
from deps_documents.infrastructure.access_management.context_vars import user

_logger = logging.getLogger("app")


def create_container(settings: Settings) -> Container:
    container = Container(messaging_driver_settings=settings.messaging_driver_settings)
    container.config.from_pydantic(settings)
    container.init_resources()
    container.wire(
        packages=(api,),
        modules=[
            auth,
        ],
    )
    container.wire(
        modules=[
            command_handlers,
            handlers,
        ],
    )
    container.domain_services_accessor.wire(
        modules=[
            handlers,
        ],
    )
    container.domain_event_publishers.wire(
        modules=[
            handlers,
        ],
    )
    container.core.wire((api.service_info,))

    return container


def configure_logging():
    logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    config = Settings()
    container = create_container(config)
    _base_service_init(container)

    app = FastAPI(
        title=constants.PROJECT_NAME,
        version="1.0.0",
        docs_url=f"{constants.BASE_API_PREFIX}{constants.SWAGGER_DOC_URL}" if config.documentation_enabled else None,
        description=constants.DESCRIPTION,
        openapi_url=f"{constants.BASE_API_PREFIX}/openapi.json" if config.documentation_enabled else None,
    )
    app.include_router(v1_router, prefix=constants.BASE_API_PREFIX)
    app.include_router(v2_router, prefix=constants.BASE_API_PREFIX)
    app.include_router(internal_router, prefix=constants.INTERNAL_API_PREFIX, include_in_schema=False)
    app.include_router(healthcheck_router, prefix=constants.BASE_API_PREFIX)
    app.include_router(service_info_router, prefix=constants.BASE_API_PREFIX)
    app.container = container  # type: ignore

    configure_logging()

    register_extensions(app, container)
    register_errorhandler(app)
    register_auth(app, container)

    container.check_dependencies()

    if container.config.instrumentation_enabled():
        from deps_observability_instrumentation import (  # noqa: WPS433
            instrument_fast_api,
        )

        instrument_fast_api(app)

    return app


def run_consumer() -> None:
    config = Settings()
    container: Container = create_container(config)
    _base_service_init(container)

    container.application.document_type().initialize()
    container.application.group().initialize()
    consumer = container.services.consumer()
    consumer.start_consuming()


def register_extensions(app, container: Container):
    app.use_cases = container.use_cases  # type: ignore
    app.services = container.application_services  # type: ignore
    app.domain_services = container.domain_services  # type: ignore
    app.domain_services_accessor = container.domain_services_accessor  # type: ignore


def register_auth(app: FastAPI, container: Container):
    if app.container.config.authentication.enabled():  # type: ignore
        add_auth_to_openapi(app)
        _logger.info(
            f"### Authentication Enabled with permission rule "
            f"`{app.container.config.authentication.document_permission_rule()}` ###",  # type: ignore   # noqa: WPS326
        )

        @app.middleware("http")
        async def auth_middleware(request: Request, call_next):  # noqa: WPS430
            try:
                auth.set_user_from_jwt(request)
            except AuthError as e:
                return json_domain_error_handler(e, HTTPStatus.UNAUTHORIZED)
            except ForbiddenError as err:
                return json_domain_error_handler(err, HTTPStatus.FORBIDDEN)
            return await call_next(request)


def _base_service_init(container: Container) -> None:
    if container.config.instrumentation_enabled():
        _logger.info("Instrumentation enabled.")
        from deps_observability_instrumentation import (  # noqa: WPS433
            instrument_external_clients,
            instrument_messaging,
            setup_instrumentation,
        )

        setup_instrumentation()
        instrument_messaging(container.messaging.producer(), container.messaging.consumer())
        instrument_external_clients(
            [
                container.services.object_storage(),
                container.services.corleone_service(),
                container.services.validation(),
            ],
        )

    if container.config.authentication.enabled():
        container.message_brokers.broker_client().user_context = user

        container.services.corleone_service().set_user_context(user)
        container.services.validation().set_user_context(user)
