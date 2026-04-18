from enum import Enum
from typing import Any, Optional

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import ConfigDict, Field, field_validator
from pydantic_settings import BaseSettings

from deps_documents.extras.datasource import DatabaseSettings
from deps_documents.extras.settings import (
    AuthenticationSettings as BaseAuthenticationSettings,
)
from deps_documents.extras.settings import ServiceInfoSettings
from deps_documents.infrastructure.access_management.constants import (
    DocumentAccessRulesEnum,
)


class BlobProviderEnum(Enum):
    internal = "internal"
    gcp = "gcp"


class FileStorageSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="file_storage_", case_sensitive=False)

    url: str = None
    external_url: str = None


class QueueSettings(BaseSettings):
    default_queue: str = "default"
    preprocess_queue: str = "preprocess"
    identification_queue: str = "identification"


class RedisSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="redis_", case_sensitive=False)

    host: str | None = None
    port: str | None = None
    db: str | None = None
    password: str | None = None


class CorleoneSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="corleone_", case_sensitive=False)

    api_host: Optional[str] = None
    api_port: Optional[str] = None
    api_endpoint: Optional[str] = None


class AuthenticationSettings(BaseAuthenticationSettings):
    create_role: str = Field(None, validation_alias="CREATE_ROLE")
    read_role: str = Field(None, validation_alias="READ_ROLE")
    write_role: str = Field(None, validation_alias="WRITE_ROLE")
    admins_group: str = Field("deps-admins", validation_alias="ADMINS_GROUP")
    document_permission_rule: DocumentAccessRulesEnum = Field(DocumentAccessRulesEnum.none, validation_alias="ACCESS_MODE")
    default_organisation: str = "deps-users"

    @field_validator("document_permission_rule")
    @classmethod
    def validate_document_permission_rule(cls, v, info):  # noqa: N805
        if v != DocumentAccessRulesEnum.none and not info.data["enabled"]:
            raise ValueError("Please enable auth to limit access to documents")
        if v == DocumentAccessRulesEnum.role:
            if not (info.data["create_role"] and info.data["write_role"] and info.data["read_role"]):
                raise ValueError("Please provide all READ, WRITE, CREATE roles")
        return v


class GCPSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="gcp_", case_sensitive=False)

    blob_storage_bucket_name: Optional[str] = None
    blob_storage_auth_key: Optional[str] = None
    media_expires: Optional[int] = None


class CloudStorageSettings(BaseSettings):
    gcp: GCPSettings = Field(default_factory=GCPSettings)


class StorageSettings(BaseSettings):
    file_storage: FileStorageSettings = Field(default_factory=FileStorageSettings)
    cloud_storage: CloudStorageSettings = Field(default_factory=CloudStorageSettings)


class PriorityManagerSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="priority_", case_sensitive=False)

    medium_boundary: int = Field(..., gt=0)
    high_boundary: int = Field(..., gt=0)

    @field_validator("high_boundary")
    @classmethod
    def validate_boundary(cls, v, info):  # noqa: N805
        if v <= info.data["medium_boundary"]:
            raise ValueError("High priority boundary should be higher than medium boundary")
        return v


class Settings(BaseSettings):
    env: str
    debug: bool = False
    testing: bool = False

    secret_key: str | None = None
    media_secret: str | None = None

    available_engines: dict = {
        "TESSERACT": "Tesseract",
        "GCP_VISION": "GCP Vision",
        "ABBYY": "ABBYY",
        "CRAFT_TESSERACT": "Craft + Tesseract",
    }

    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    authentication: AuthenticationSettings = Field(default_factory=AuthenticationSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    postgres: DatabaseSettings = Field(default_factory=DatabaseSettings)
    queue: QueueSettings = Field(default_factory=QueueSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    corleone: CorleoneSettings = Field(default_factory=CorleoneSettings)
    priority: PriorityManagerSettings = Field(default_factory=PriorityManagerSettings)

    messaging_driver: MessagingDriverEnum = Field(MessagingDriverEnum.RABBITMQ, validation_alias="MESSAGING_DRIVER")
    messaging_driver_settings: Any = Field(None, validation_alias="MESSAGING_DRIVER_SETTINGS")
    message_broker_connection_string: str

    service_version: ServiceInfoSettings = Field(default_factory=ServiceInfoSettings)

    validation_api_url: str

    parsing_enabled: bool = False
    documentation_enabled: bool = True
    auto_validation_enabled: bool = False

    reviewer_reassign_enabled: bool = False

    instrumentation_enabled: bool = False

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("messaging_driver_settings")
    @classmethod
    def validate_messaging_driver_settings(cls, v, info):  # noqa: N805
        messaging_driver = info.data.get("messaging_driver")
        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().model_dump()  # TODO: use BaseSettings

        raise ValueError(f"Driver {driver} is not implemented")
