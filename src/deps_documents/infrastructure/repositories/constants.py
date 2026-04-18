from enum import Enum, auto


class DBErrorTypeEnum(Enum):
    FOREIGN_KEY_VIOLATION = auto()
    UNIQUE_VIOLATION = auto()


# according https://www.postgresql.org/docs/current/errcodes-appendix.html
class PostgresErrorCodeEnum(Enum):
    FOREIGN_KEY_VIOLATION = "23503"
    UNIQUE_VIOLATION = "23505"
