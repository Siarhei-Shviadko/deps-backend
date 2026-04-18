import datetime

import pytest

from deps_documents.domain.constants import TimePeriodEnum
from deps_documents.domain.dtos import DateTimeRangeObject, DocumentTypeChangeFilter


@pytest.fixture()
def mocked_analytics_service(mocker, domain_services):
    analytics_service_mock = mocker.Mock(domain_services.analytics.cls)
    analytics_service_mock.aggregate_document_type_change.return_value = []
    domain_services.analytics.override(analytics_service_mock)

    return analytics_service_mock


@pytest.mark.usefixtures("mocked_analytics_service")
class TestAnalyticsAggregateDocumentTypeChangeView:
    def test_get__no_params__return_200(self, client):
        response = client.get("/api/document/v1/analytics/document-type-change")

        assert response.status_code == 200
        assert response.json()

    def test_get__all_valid_params__return_200(self, client):
        response = client.get(
            "/api/document/v1/analytics/document-type-change",
            params={
                "fromType": "SomeOldType",
                "toType": "SomeNewType",
                "changedBy": "user",
                "dateRange": ["2019-08-15T10:00:00.000Z", "2019-08-16T10:00:00.000Z"],
                "aggregationPeriod": "hour",
            },
        )

        assert response.status_code == 200

    def test_get__invalid_date_range_format__return_422(self, client):
        response = client.get(
            "/api/document/v1/analytics/document-type-change",
            params={
                "dateRange": [
                    "2019-08-15T10:00:00.000Z",
                ]
            },
        )

        assert response.status_code == 422

    def test_get__parses_arguments_correctly(self, client, mocked_analytics_service):
        expected_date_range = DateTimeRangeObject(
            start=datetime.datetime(2019, 8, 15, 10, 0, 0, 0), end=datetime.datetime(2019, 8, 16, 10, 0, 0, 0)
        )
        expected_filter_obj = DocumentTypeChangeFilter(
            old_type="SomeOldType",
            new_type="SomeNewType",
            changed_by="user",
            date_range=expected_date_range,
            aggregation_period=TimePeriodEnum.DAY,
        )

        client.get(
            "/api/document/v1/analytics/document-type-change",
            params={
                "fromType": "SomeOldType",
                "toType": "SomeNewType",
                "changedBy": "user",
                "dateRange": ["2019-08-15T10:00:00.000Z", "2019-08-16T10:00:00.000Z"],
                "aggregationPeriod": "day",
            },
        )

        assert mocked_analytics_service.aggregate_document_type_change.call_args(expected_filter_obj)

    def test_get__aggregation_period_default_is_hour(self, client, mocked_analytics_service):
        expected_filter_obj = DocumentTypeChangeFilter(aggregation_period=TimePeriodEnum.DAY)
        client.get("/api/document/v1/analytics/document-type-change")

        assert mocked_analytics_service.aggregate_document_type_change.call_args(expected_filter_obj)

    def test_get__bad_datetime_format_range___status_code_422(self, client):
        response = client.get(
            "/api/document/v1/analytics/document-type-change", params={"dateRange": ["2018-03-89T", "2019-15-42T02:00:00.000Z"]}
        )
        assert response.status_code == 422
