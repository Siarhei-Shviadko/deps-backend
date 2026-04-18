import datetime
from typing import Any, List

from sqlalchemy import DateTime, func, literal_column, select
from sqlalchemy.engine import Connection

from deps_documents.domain.constants import DocumentLogEnum, TimePeriodEnum
from deps_documents.domain.dtos import (
    DocumentTypeChangeAggregation,
    DocumentTypeChangeFilter,
)
from deps_documents.domain.interfaces import IAnalyticsRepository
from deps_documents.infrastructure.models import document_log_table


class AnalyticsRepository(IAnalyticsRepository):
    def __init__(self, connection: Connection):
        self._connection = connection

    def get_document_type_changes(self, filters: DocumentTypeChangeFilter) -> List[DocumentTypeChangeAggregation]:
        data_columns = self._get_log_columns_for_aggregation(filters.aggregation_period)
        query = select([func.count(), *data_columns])
        query = self._apply_doc_type_change_filter(query, filters)
        data_column_names = [entry.name for entry in data_columns]
        query = query.group_by(*data_column_names)

        query_result = self._connection.execute(query).fetchall()

        return self._process_doc_type_change_query_result(query_result)

    @staticmethod
    def _get_log_columns_for_aggregation(aggregation_period: TimePeriodEnum) -> List[Any]:
        columns = [
            document_log_table.c.previous,
            document_log_table.c.current,
            document_log_table.c.actor,
            func.extract("year", document_log_table.c.created_at).label("year_of_change"),
            func.extract("month", document_log_table.c.created_at).label("month_of_change"),
            func.extract("day", document_log_table.c.created_at).label("day_of_change"),
        ]
        if aggregation_period == TimePeriodEnum.HOUR:
            columns.append(func.extract("hour", document_log_table.c.created_at).label("hour_of_change"))
        else:
            columns.append(literal_column("0").label("hour_of_change"))

        return columns

    @staticmethod
    def _process_doc_type_change_query_result(query_result: List[Any]) -> List[DocumentTypeChangeAggregation]:
        aggregation_result = []
        for row in query_result:
            date_args = list(map(int, row[4:]))
            doc_type_aggregation = DocumentTypeChangeAggregation(
                number_of_changed_docs=row[0],
                previous_document_type=row[1],
                current_document_type=row[2],
                changed_by=row[3],
                date_time=datetime.datetime(date_args[0], date_args[1], date_args[2], date_args[3]),
            )
            aggregation_result.append(doc_type_aggregation)

        return aggregation_result

    @staticmethod
    def _apply_doc_type_change_filter(query, filters: DocumentTypeChangeFilter):
        query = query.where(document_log_table.c.action == DocumentLogEnum.TYPE_CHANGED.value)
        if filters.old_type:
            query = query.where(document_log_table.c.previous == filters.old_type)
        if filters.new_type:
            query = query.where(document_log_table.c.current == filters.new_type)
        if filters.changed_by:
            query = query.where(document_log_table.c.actor == filters.changed_by)
        if filters.date_range:
            if filters.date_range.start:
                query = query.where(document_log_table.c.created_at.cast(DateTime) >= filters.date_range.start)
            if filters.date_range.end:
                query = query.where(document_log_table.c.created_at.cast(DateTime) < filters.date_range.end)
        return query
