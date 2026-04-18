from datetime import datetime

from deps_documents.domain.constants import DocumentPriorityEnum
from deps_documents.domain.entities import DocumentEntity
from deps_documents.domain.interfaces import IPriorityManager


class TimeInProcessingPriorityManager(IPriorityManager):
    def __init__(self, medium_priority_boundary: int, high_priority_boundary: int):
        # Border values in seconds
        self._medium_priority_boundary = medium_priority_boundary
        self._high_priority_boundary = high_priority_boundary

    def get_priority(self, document_entity: DocumentEntity) -> DocumentPriorityEnum:
        spent_time = self._get_spent_time(document_entity.date)
        if self._medium_priority_boundary <= spent_time < self._high_priority_boundary:
            priority = DocumentPriorityEnum.MEDIUM
        elif spent_time > self._high_priority_boundary:
            priority = DocumentPriorityEnum.HIGH
        else:
            priority = DocumentPriorityEnum.LOW

        return priority

    @staticmethod
    def _get_spent_time(created_date: datetime) -> int:
        return (datetime.now(tz=created_date.tzinfo) - created_date).seconds
