import pytest

from deps_documents.domain.constants import FieldTypeEnum

VALUE_MAP = {
    FieldTypeEnum.STRING: "pystr",
    FieldTypeEnum.NUMBER: "pyfloat",
    FieldTypeEnum.DATETIME: "date_time_between",
    FieldTypeEnum.DATE: "date_between",
    FieldTypeEnum.TIME: "time",
}


def sort_by_order_and_name(fields):
    return sorted(fields, key=lambda field: (field.order, field.name))
