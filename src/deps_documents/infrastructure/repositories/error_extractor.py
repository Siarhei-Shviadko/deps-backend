import logging
from dataclasses import dataclass

from sqlalchemy.exc import DatabaseError

from deps_documents.extras.datasource import DBDriver
from deps_documents.infrastructure.repositories.constants import (
    DBErrorTypeEnum,
    PostgresErrorCodeEnum,
)

logger = logging.getLogger(__name__)


@dataclass
class DatabaseErrorContext:
    error_type: DBErrorTypeEnum
    constraint_name: str


def extract_database_error_context(err: DatabaseError, driver: str) -> DatabaseErrorContext:
    if driver == DBDriver.PG8000.value:
        return DatabaseErrorContext(
            error_type=convert_pgcode_to_error_type(err.orig.args[0]["C"]),
            constraint_name=err.orig.args[0]["n"],
        )
    elif driver == DBDriver.PSYCOPG2.value:
        return DatabaseErrorContext(
            error_type=convert_pgcode_to_error_type(err.orig.pgcode),
            constraint_name=err.orig.diag.constraint_name,
        )

    logger.warning(f"Unsupported database driver '{driver}' during extracting error type")
    raise


def convert_pgcode_to_error_type(code: str) -> DBErrorTypeEnum:
    code2error_type = {
        PostgresErrorCodeEnum.UNIQUE_VIOLATION.value: DBErrorTypeEnum.UNIQUE_VIOLATION,
        PostgresErrorCodeEnum.FOREIGN_KEY_VIOLATION.value: DBErrorTypeEnum.FOREIGN_KEY_VIOLATION,
    }

    if code not in code2error_type:
        raise

    return code2error_type[code]
