from datetime import datetime, timedelta, timezone

import pytest

from deps_documents.domain.constants import DocumentPriorityEnum
from deps_documents.domain.priority_managers import TimeInProcessingPriorityManager
from tests.factories import DocumentEntityFactory

MEDIUM_BOUNDARY = 3600
HIGH_BOUNDARY = 10000


@pytest.mark.priority
class TestTimePriorityManager:
    @pytest.mark.parametrize(
        ["create_date", "priority"],
        [
            (datetime.now(tz=timezone.utc), DocumentPriorityEnum.LOW),
            (datetime.now(tz=timezone.utc) - timedelta(seconds=MEDIUM_BOUNDARY + 20), DocumentPriorityEnum.MEDIUM),
            (datetime.now(tz=timezone.utc) - timedelta(seconds=HIGH_BOUNDARY + 20), DocumentPriorityEnum.HIGH),
        ],
    )
    def test_get_priority__many_spent_time__return_appropriate_priority(
        self, create_date: datetime, priority: DocumentPriorityEnum
    ):
        priority_manager = TimeInProcessingPriorityManager(MEDIUM_BOUNDARY, HIGH_BOUNDARY)
        document_entity = DocumentEntityFactory(date=create_date)

        res = priority_manager.get_priority(document_entity)

        assert res == priority
