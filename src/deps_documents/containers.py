from typing import Any, Dict, Optional, Type, Union

from dependency_injector import containers, providers, resources
from deps_asb import ASBClient, ASBConsumer, ASBProducer
from deps_kafka import KafkaClient, KafkaConsumer, KafkaProducer
from deps_message_flow import MessagingDriverEnum
from deps_message_flow.commands.producer import CommandProducer
from deps_message_flow.events.publisher import DomainEventPublisher
from deps_message_flow.messaging.consumer import IMessageConsumer
from deps_message_flow.messaging.producer import IMessageProducer
from deps_object_storage import ObjectStorage, make_object_storage
from deps_rabbitmq import RabbitMQClient, RabbitMQConsumer, RabbitMQProducer

from deps_documents.application import (
    DocumentAccessServiceV2,
    DocumentAccessServiceV3,
    DocumentServiceV2,
    DocumentServiceV3,
    DocumentTypeService,
    GroupService,
)
from deps_documents.constants import PROJECT_NAME
from deps_documents.domain.priority_managers import TimeInProcessingPriorityManager
from deps_documents.domain.services import (
    AnalyticsService,
    DocumentFileService,
    DocumentLogService,
    DocumentService,
    LabelService,
    RelationService,
)
from deps_documents.domain.use_cases.batch_upload import (
    CreateUploadSessionDataUseCase,
    GetBatchUploadDataUseCase,
    UpdateBatchUploadDataUseCase,
)
from deps_documents.domain.use_cases.services import (
    AcceptPreprocessResultUseCase,
    ApplyClassificationResultUseCase,
    BeginExtractionUseCase,
    BeginPreprocessUseCase,
    ReviewUseCase,
    ServiceFailedUseCase,
    ServiceSucceededUseCase,
    StartClassificationUseCase,
)
from deps_documents.events_handler.consumer import make_consumer
from deps_documents.extras.auth import (
    APIKeyAuthService,
    DepsAuthService,
    JWTAuthService,
)
from deps_documents.extras.datasource import Database, DBDialect, DBDriver
from deps_documents.infrastructure.access_management.context_vars import user
from deps_documents.infrastructure.access_management.document_access_manager import (
    DocumentServiceAccessManagerTrap,
    GroupBasedDocumentServiceAccessManager,
    OrganisationBasedDocumentServiceAccessManager,
    RoleBasedDocumentServiceAccessManager,
    UserBasedDocumentServiceAccessManager,
)
from deps_documents.infrastructure.access_management.document_service_accessor import (
    DocumentServiceAccessor,
)
from deps_documents.infrastructure.access_management.label_access_manager import (
    LabelServiceAccessManagerTrap,
    OrganisationBasedLabelServiceAccessManager,
)
from deps_documents.infrastructure.access_management.label_service_accessor import (
    LabelServiceAccessor,
)
from deps_documents.infrastructure.document_uow import DocumentUnitOfWork
from deps_documents.infrastructure.repositories import (
    AnalyticsRepository,
    BatchUploadDataRepository,
    CommentRepository,
    DocumentEntityRepository,
    DocumentLogEntityRepository,
    DocumentTypeRepository,
    GroupRepository,
    LabelRepository,
    RelationRepository,
)
from deps_documents.infrastructure.services import (
    ChoreographyManager,
    CorleoneService,
    FileUrlService,
    ValidationService,
)
from deps_documents.infrastructure.synchronisation import SynchronisationRegistry

MessagingClient = Union[ASBClient, KafkaClient, RabbitMQClient]


class DatabaseResource(resources.Resource):
    def init(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        database: str,
        dialect: DBDialect,
        driver: DBDriver,
        require_secure_transport: bool,
        sslkey: str,
        sslcert: str,
        sslrootcert: str,
        sslmode: str,
    ) -> Database:
        db = Database(
            username=username,
            password=password,
            host=host,
            port=port,
            database=database,
            dialect=dialect,
            driver=driver,
            require_secure_transport=require_secure_transport,
            sslkey=sslkey,
            sslcert=sslcert,
            sslrootcert=sslrootcert,
            sslmode=sslmode,
        )
        db.connect()
        return db

    def shutdown(self, resource: Database) -> None:
        resource.close()


class MessageBrokerResource(resources.Resource):
    def init(
        self,
        driver_type: str,
        expected_driver: str,
        client: Type[MessagingClient],
        message_connection_string: str,
        **kwargs: Dict[str, Any],
    ) -> Optional[MessagingClient]:
        return client(message_connection_string, **kwargs) if driver_type == expected_driver else None

    def shutdown(self, resource: Optional[MessagingClient]) -> None:
        if resource:
            resource.close()


class MessageBrokers(containers.DeclarativeContainer):
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    broker_client: providers.Provider[MessagingClient] = providers.Selector(
        config.messaging_driver,
        asb=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.ASB.value,
            expected_driver=config.messaging_driver,
            client=ASBClient,
            message_connection_string=config.message_broker_connection_string,
            asb_settings=messaging_driver_settings,
        ),
        kafka=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.KAFKA.value,
            expected_driver=config.messaging_driver,
            client=KafkaClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
        rabbitmq=providers.Resource(
            MessageBrokerResource,
            driver_type=MessagingDriverEnum.RABBITMQ.value,
            expected_driver=config.messaging_driver,
            client=RabbitMQClient,
            message_connection_string=config.message_broker_connection_string,
            settings=messaging_driver_settings,
        ),
    )


class Datasources(containers.DeclarativeContainer):
    config = providers.Configuration()

    postgres_datasource: providers.Provider[Database] = providers.Resource(
        DatabaseResource,
        username=config.postgres.user,
        password=config.postgres.password,
        host=config.postgres.host,
        port=config.postgres.port,
        database=config.postgres.db,
        dialect=config.postgres.dialect,
        driver=config.postgres.driver,
        require_secure_transport=config.postgres.require_secure_transport,
        sslkey=config.postgres.ssl.key,
        sslcert=config.postgres.ssl.cert,
        sslrootcert=config.postgres.ssl.rootcert,
        sslmode=config.postgres.ssl.mode,
    )


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()
    build_info: providers.Provider[Dict] = providers.Dict(
        {
            "build_tag": config.service_version.tag,
            "build_date": config.service_version.date,
            "commit_hash": config.service_version.hash,
        },
    )


class Messaging(containers.DeclarativeContainer):
    config = providers.Configuration()
    message_brokers = providers.DependenciesContainer()

    producer: providers.Provider[IMessageProducer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBProducer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
        ),
        kafka=providers.Singleton(
            KafkaProducer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQProducer,
            client=message_brokers.broker_client,
        ),
    )
    consumer: providers.Provider[IMessageConsumer] = providers.Selector(
        config.messaging_driver,
        asb=providers.Singleton(
            ASBConsumer,
            client=message_brokers.broker_client,
            topic_name=config.messaging_driver_settings.topic_name,
            custom_subscription_name=PROJECT_NAME,
        ),
        kafka=providers.Singleton(
            KafkaConsumer,
            client=message_brokers.broker_client,
        ),
        rabbitmq=providers.Singleton(
            RabbitMQConsumer,
            client=message_brokers.broker_client,
        ),
    )


class DomainEventPublishers(containers.DeclarativeContainer):
    messaging = providers.DependenciesContainer()

    publisher: providers.Singleton[DomainEventPublisher] = providers.Singleton(
        DomainEventPublisher,
        messaging.producer,
    )


class CommandProducers(containers.DeclarativeContainer):
    messaging = providers.DependenciesContainer()

    producer: providers.Singleton[CommandProducer] = providers.Singleton(
        CommandProducer,
        messaging.producer,
    )


class Repositories(containers.DeclarativeContainer):
    config = providers.Configuration()

    analytics = providers.Factory(
        AnalyticsRepository,
    )
    batch_upload_data = providers.Factory(
        BatchUploadDataRepository,
        config.redis.host,
        config.redis.port,
        config.redis.db,
        config.redis.password,
    )
    label = providers.Factory(
        LabelRepository,
    )
    relation = providers.Factory(
        RelationRepository,
    )
    comment = providers.Factory(
        CommentRepository,
    )
    document = providers.Factory(
        DocumentEntityRepository,
    )
    document_log = providers.Factory(
        DocumentLogEntityRepository,
    )
    document_type = providers.Factory(
        DocumentTypeRepository,
    )
    group = providers.Factory(
        GroupRepository,
    )


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()
    units_of_work = providers.DependenciesContainer()
    messaging = providers.DependenciesContainer()
    domain_event_publishers = providers.DependenciesContainer()

    object_storage: providers.Provider[ObjectStorage] = providers.Singleton(make_object_storage)

    pipeline_manager = providers.Singleton(
        ChoreographyManager,
        domain_event_publishers.publisher,
    )

    jwt_auth_service = providers.Singleton(
        JWTAuthService,
        config.authentication.certs_endpoint,
        config.authentication.encryption_algorithm,
        config.authentication.verify_ssl,
    )

    api_key_auth_service: providers.Singleton[APIKeyAuthService] = providers.Singleton(
        APIKeyAuthService,
        config.authentication.api_key,
    )

    deps_auth_service = providers.Singleton(
        DepsAuthService,
        jwt_auth_service,
        api_key_auth_service,
    )

    corleone_service = providers.Singleton(
        CorleoneService,
        config.corleone.api_host,
        config.corleone.api_port,
        config.corleone.api_endpoint,
    )

    consumer: providers.Singleton[IMessageConsumer] = providers.Singleton(
        make_consumer,
        messaging.consumer,
        messaging.producer,
        config.parsing_enabled,
    )

    validation = providers.Singleton(ValidationService, config.validation_api_url)


class ApplicationServices(containers.DeclarativeContainer):
    """Contain services used in the views layer"""

    config = providers.Configuration()

    file_url = providers.Singleton(
        FileUrlService,
        config.storage.file_storage.external_url,
        config.storage.file_storage.url,
    )


class PriorityManagers(containers.DeclarativeContainer):
    config = providers.Configuration()

    time_in_processing = providers.Singleton(
        TimeInProcessingPriorityManager,
        config.priority.medium_boundary,
        config.priority.high_boundary,
    )


class DomainServices(containers.DeclarativeContainer):
    config = providers.Configuration()
    services = providers.DependenciesContainer()
    priority_managers = providers.DependenciesContainer()
    units_of_work = providers.DependenciesContainer()
    document_type_service = providers.Dependency(instance_of=object)

    analytics = providers.Factory(
        AnalyticsService,
        uow=units_of_work.uow.provider,
    )
    document = providers.Factory(
        DocumentService,
        priority_manager=priority_managers.time_in_processing,
        validation_service=services.validation,
        corleone_service=services.corleone_service,
        document_type_service=document_type_service,
        pipeline_manager=services.pipeline_manager,
        blob_service=services.object_storage,
        uow=units_of_work.uow.provider,
    )
    document_log = providers.Factory(DocumentLogService, units_of_work.uow.provider)
    document_file = providers.Factory(
        DocumentFileService,
        services.object_storage,
    )
    label = providers.Factory(
        LabelService,
        uow=units_of_work.uow.provider,
    )
    relation = providers.Factory(
        RelationService,
        units_of_work.uow.provider,
        document,
    )


class DomainServicesAccessor(containers.DeclarativeContainer):
    domain_services = providers.DependenciesContainer()
    document_service_access_manager = providers.DependenciesContainer()
    label_service_access_manager = providers.DependenciesContainer()

    document = providers.Factory(
        DocumentServiceAccessor,
        domain_services.document,
        document_service_access_manager,
        label_service_access_manager,
    )

    label = providers.Factory(
        LabelServiceAccessor,
        domain_services.label,
        label_service_access_manager,
    )


class UseCases(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()
    services = providers.DependenciesContainer()
    domain_services_accessor = providers.DependenciesContainer()
    units_of_work = providers.DependenciesContainer()

    # batch upload use cases
    create_upload_session = providers.Factory(
        CreateUploadSessionDataUseCase,
        repositories.batch_upload_data,
    )

    get_batch_upload_data = providers.Factory(
        GetBatchUploadDataUseCase,
        repositories.batch_upload_data,
    )

    update_batch_upload_data = providers.Factory(
        UpdateBatchUploadDataUseCase,
        repositories.batch_upload_data,
    )

    service_failed = providers.Factory(ServiceFailedUseCase, units_of_work.uow.provider)
    service_succeeded = providers.Factory(ServiceSucceededUseCase, domain_services_accessor.document)
    service_begin_preprocess_document = providers.Factory(BeginPreprocessUseCase, units_of_work.uow.provider)
    service_preprocess_document = providers.Factory(
        AcceptPreprocessResultUseCase,
        domain_services_accessor.document,
        services.object_storage,
        services.pipeline_manager,
    )
    service_start_classification = providers.Factory(StartClassificationUseCase, units_of_work.uow.provider)
    service_classify_document = providers.Factory(ApplyClassificationResultUseCase, units_of_work.uow.provider)
    service_begin_extraction = providers.Factory(BeginExtractionUseCase, units_of_work.uow.provider)
    service_review_document = providers.Factory(ReviewUseCase, units_of_work.uow.provider)


class UnitsOfWork(containers.DeclarativeContainer):
    datasources = providers.DependenciesContainer()
    repositories = providers.DependenciesContainer()
    domain_event_publishers = providers.DependenciesContainer()
    uow = providers.Factory(
        DocumentUnitOfWork,
        database=datasources.postgres_datasource,
        event_publisher=domain_event_publishers.publisher,
        comment_repo_factory=repositories.comment.provider,
        document_repo_factory=repositories.document.provider,
        document_log_repo_factory=repositories.document_log.provider,
        analytics_repo_factory=repositories.analytics.provider,
        label_repo_factory=repositories.label.provider,
        relation_repo_factory=repositories.relation.provider,
        document_type_repo_factory=repositories.document_type.provider,
        group_repo_factory=repositories.group.provider,
    )


class Synchronisation(containers.DeclarativeContainer):
    registry = providers.Singleton(
        SynchronisationRegistry,
    )


class Application(containers.DeclarativeContainer):
    units_of_work = providers.DependenciesContainer()
    document_service_access_manager = providers.DependenciesContainer()
    command_producers = providers.DependenciesContainer()
    services = providers.DependenciesContainer()

    document_type = providers.Singleton(
        DocumentTypeService,
        uow=units_of_work.uow.provider,
        command_producer=command_producers.producer,
    )

    group = providers.Singleton(
        GroupService,
        uow=units_of_work.uow.provider,
        command_producer=command_producers.producer,
    )

    document: providers.Factory[DocumentServiceV2] = providers.Factory(
        DocumentServiceV2,
        uow=units_of_work.uow.provider,
        document_type_service=document_type,
    )
    document_access: providers.Factory[DocumentAccessServiceV2] = providers.Factory(
        DocumentAccessServiceV2,
        document,
        document_service_access_manager,
    )

    document_v3: providers.Factory[DocumentServiceV3] = providers.Factory(
        DocumentServiceV3,
        uow=units_of_work.uow.provider,
        file_storage=services.object_storage,
        command_producer=command_producers.producer,
    )
    document_access_v3: providers.Factory[DocumentAccessServiceV3] = providers.Factory(
        DocumentAccessServiceV3,
        document_v3,
        document_service_access_manager,
    )


class Container(containers.DeclarativeContainer):
    current_user_tenant = providers.Callable(lambda: user.get()["organisation"])
    config = providers.Configuration()
    messaging_driver_settings = providers.Dependency(instance_of=object)

    datasources: providers.Container[Datasources] = providers.Container(Datasources, config=config)

    message_brokers: providers.Container[MessageBrokers] = providers.Container(
        MessageBrokers,
        config=config,
        messaging_driver_settings=messaging_driver_settings,
    )
    messaging: providers.Container[Messaging] = providers.Container(Messaging, config=config, message_brokers=message_brokers)
    domain_event_publishers: providers.Container[DomainEventPublishers] = providers.Container(
        DomainEventPublishers,
        messaging=messaging,
    )
    command_producers: providers.Container[CommandProducers] = providers.Container(CommandProducers, messaging=messaging)

    core: providers.Container[Core] = providers.Container(Core, config=config)

    repositories: providers.Container[Repositories] = providers.Container(
        Repositories,
        config=config,
    )
    units_of_work: providers.Container[UnitsOfWork] = providers.Container(
        UnitsOfWork,
        datasources=datasources,
        domain_event_publishers=domain_event_publishers,
        repositories=repositories,
    )

    services: providers.Container[Services] = providers.Container(
        Services,
        config=config,
        units_of_work=units_of_work,
        messaging=messaging,
        domain_event_publishers=domain_event_publishers,
    )

    application_services: providers.Container[ApplicationServices] = providers.Container(
        ApplicationServices,
        config=config,
    )

    priority_managers: providers.Container[PriorityManagers] = providers.Container(PriorityManagers, config=config)

    document_service_access_manager = providers.Selector(
        config.authentication.document_permission_rule,
        none=providers.Singleton(DocumentServiceAccessManagerTrap),
        user=providers.Factory(UserBasedDocumentServiceAccessManager, units_of_work.uow.provider),
        role=providers.Singleton(
            RoleBasedDocumentServiceAccessManager,
            config.authentication.create_role,
            config.authentication.read_role,
            config.authentication.write_role,
        ),
        group=providers.Singleton(
            GroupBasedDocumentServiceAccessManager,
            units_of_work.uow.provider,
            config.authentication.admins_group,
        ),
        organisation=providers.Singleton(
            OrganisationBasedDocumentServiceAccessManager,
            units_of_work.uow.provider,
        ),
    )

    label_service_access_manager = providers.Selector(
        config.authentication.document_permission_rule,
        none=providers.Singleton(LabelServiceAccessManagerTrap),
        user=providers.Singleton(OrganisationBasedLabelServiceAccessManager, units_of_work.uow.provider),
        role=providers.Singleton(OrganisationBasedLabelServiceAccessManager, units_of_work.uow.provider),
        group=providers.Singleton(OrganisationBasedLabelServiceAccessManager, units_of_work.uow.provider),
        organisation=providers.Singleton(OrganisationBasedLabelServiceAccessManager, units_of_work.uow.provider),
    )

    application: providers.Container[Application] = providers.Container(
        Application,
        units_of_work=units_of_work,
        document_service_access_manager=document_service_access_manager,
        command_producers=command_producers,
        services=services,
    )

    domain_services: providers.Container[DomainServices] = providers.Container(
        DomainServices,
        config=config,
        services=services,
        priority_managers=priority_managers,
        units_of_work=units_of_work,
        document_type_service=application.document_type,
    )
    domain_services_accessor: providers.Container[DomainServicesAccessor] = providers.Container(
        DomainServicesAccessor,
        domain_services=domain_services,
        document_service_access_manager=document_service_access_manager,
        label_service_access_manager=label_service_access_manager,
    )

    use_cases: providers.Container[UseCases] = providers.Container(
        UseCases,
        repositories=repositories,
        services=services,
        domain_services_accessor=domain_services_accessor,
        units_of_work=units_of_work,
    )

    synchronisaction: providers.Container[Synchronisation] = providers.Container(
        Synchronisation,
    )
