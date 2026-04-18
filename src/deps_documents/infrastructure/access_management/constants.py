from enum import Enum


class DocumentAccessRulesEnum(str, Enum):
    none = "none"
    user = "user"
    role = "role"
    group = "group"
    organisation = "organisation"
