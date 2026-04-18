from typing import List, Union

from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.exceptions import PrimaryKeyError


def cast_to_db_pk(pk: Union[str, DocumentEntityPk]):
    try:
        return int(pk)
    except ValueError:
        raise PrimaryKeyError("Could not cast ID to int: ", pk)


def cast_from_db_pk(pk: int):
    return str(pk)


def batch_pk_validate(document_pks: List[DocumentEntityPk]) -> List[DocumentEntityPk]:
    valid_document_pks = []

    for value in document_pks:
        pk_is_int = cast_to_db_pk(value)
        valid_document_pks.append(pk_is_int)

    return valid_document_pks


def escape_special_chars(s: str, escape_char: str = "\\") -> str:
    escaped_s = s.replace(escape_char, escape_char * 2)
    return escaped_s.replace("%", f"{escape_char}%").replace("_", f"{escape_char}_")
