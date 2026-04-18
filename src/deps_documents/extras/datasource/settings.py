from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings

from .constants import DBDialect, DBDriver

__all__ = ["DatabaseSettings"]


class SSLSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="DATABASE_SSL")

    key: str = ""
    cert: str = ""
    rootcert: str = ""
    mode: str = "verify-full"


class DatabaseSettings(BaseSettings):
    model_config = ConfigDict(env_prefix="DATABASE_")

    user: str
    password: str
    host: str
    port: str
    db: str
    ssl: SSLSettings = Field(default_factory=SSLSettings)
    dialect: DBDialect = DBDialect.POSTGRES
    driver: DBDriver = DBDriver.PSYCOPG2
    require_secure_transport: bool = False
