from datetime import datetime

import pytest

from deps_documents.domain.dtos import (
    DocumentTypeChangeAggregation,
    DocumentTypeChangeFilter,
)


@pytest.fixture
def domain_services(domain_services):
    domain_services.analytics.reset_override()

    return domain_services


class TestAnalyticsService:
    def test_aggregate_document_type_change__valid_input__return_aggregate_result(self, domain_services, uow):
        uow.analytics.get_document_type_changes.return_value = [
            DocumentTypeChangeAggregation(
                date_time=datetime(2020, 1, 1, 0, 0, 0),
                number_of_changed_docs=1,
                changed_by="Test Name",
                previous_document_type="a",
                current_document_type="b",
            )
        ]

        result = domain_services.analytics().aggregate_document_type_change(
            DocumentTypeChangeFilter(old_type="a", new_type="b", changed_by="Test Name")
        )

        assert result == [
            DocumentTypeChangeAggregation(
                date_time=datetime(2020, 1, 1, 0, 0, 0),
                number_of_changed_docs=1,
                changed_by="Test Name",
                previous_document_type="a",
                current_document_type="b",
            )
        ]
