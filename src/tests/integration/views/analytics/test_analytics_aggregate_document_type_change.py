import datetime

import pytest

from deps_documents.domain.constants import ActorEnum, DocumentLogEnum
from deps_documents.domain.dtos import DateTimeRangeObject, DocumentTypeChangeFilter
from tests.factories import DocumentEntityFactory, DocumentLogEntityFactory


@pytest.mark.skip
class TestAnalyticsAggregateDocumentTypeChange:
    def test_get__with_some_filter__status_code_200(self, client, uow):
        self._create_data(uow)
        response = client.get("/api/document/v1/analytics/document-type-change?fromType=None")
        assert response.status_code == 200

    def test_get__without_filter__return_data_grouped_by_hour(self, client, uow):
        self._create_data(uow)
        response = client.get("/api/document/v1/analytics/document-type-change")
        response_json = response.json()
        assert len(response_json["data"]) == 3

    def test_get__aggregate_period_hour__return_data_grouped_by_hour(self, client, uow):
        self._create_data(uow)
        response = client.get("/api/document/v1/analytics/document-type-change?aggregationPeriod=hour")
        response_json = response.json()
        assert len(response_json["data"]) == 3

    def test_get__aggregate_period_day__return_data_grouped_by_day(self, client, uow):
        self._create_data(uow)
        response = client.get("/api/document/v1/analytics/document-type-change?aggregationPeriod=day")
        response_json = response.json()
        assert len(response_json["data"]) == 2

    def test_get__filter_by_previous_type__return_data(self, client, uow):
        self._create_data(uow)
        response = client.get("/api/document/v1/analytics/document-type-change?fromType=None")
        response_json = response.json()
        assert len(response_json["data"]) == 2

    def test_get__filter_by_current_type___return_data(self, client, uow):
        self._create_data(uow)
        response = client.get("/api/document/v1/analytics/document-type-change?toType=BelarusPassport")
        response_json = response.json()
        assert len(response_json["data"]) == 2

    def test_get__filter_by_date_range__return_data(self, client, uow):
        self._create_data(uow)
        response = client.get(
            "/api/document/v1/analytics/document-type-change?dateRange=" '["2019-08-15T08:00:00.000Z","2019-08-15T10:31:00.000Z"]'
        )
        response_json = response.json()
        assert len(response_json["data"]) == 2

    def test_get__filter_by_actor__return_data(self, client, uow):
        self._create_data(uow)
        response = client.get("/api/document/v1/analytics/document-type-change?changedBy=manual")
        response_json = response.json()
        assert len(response_json["data"]) == 1

    def test_get__filter_by_all_params__return_data(self, client, uow):
        self._create_data(uow)
        response = client.get(
            "/api/document/v1/analytics/document-type-change"
            "?fromType=None"
            "&toType=BelarusPassport"
            '&dateRange=["2019-08-15T08:00:00.000Z","2019-08-15T10:31:00.000Z"]'
            "&changedBy=automatic"
        )
        response_json = response.json()
        assert len(response_json["data"]) == 1

    def test_get__filter_no_data__return_no_data(self, client, uow):
        self._create_data(uow)
        response = client.get("/api/document/v1/analytics/document-type-change?fromType=None&toType=DirectionalSurvey")
        response_json = response.json()
        assert len(response_json["data"]) == 0

    def test_get__empty_database__status_200(self, client):
        response = client.get("/api/document/v1/analytics/document-type-change?fromType=None&toType=DirectionalSurvey")
        assert response.status_code == 200

    def test_get__empty_database__return_empty_data(self, client):
        response = client.get("/api/document/v1/analytics/document-type-change?fromType=None&toType=DirectionalSurvey")
        response_json = response.json()
        assert len(response_json["data"]) == 0

    def test_get__bad_datetime_format_range___status_code_422(self, client, uow):
        self._create_data(uow)
        response = client.get(
            "/api/document/v1/analytics/document-type-change" '?dateRange=["2018-03-89T","2019-15-42T02:00:00.000Z"]'
        )
        assert response.status_code == 422

    def test_get__not_full_daterange_param__status_code_422(self, client, uow):
        response = client.get('/api/document/v1/analytics/document-type-change?dateRange=["2019-08-15T10:00:00.000Z",]')
        assert response.status_code == 422

    def _create_data(self, uow):
        document1 = uow.document.add(DocumentEntityFactory(document_type="code1"))
        document2 = uow.document.add(DocumentEntityFactory(document_type="code2"))

        # log entries 0 and 2 are the same within the same hour so they should grouped into one
        document_log_entities = [
            DocumentLogEntityFactory(
                document_id=document1.pk,
                action=DocumentLogEnum.TYPE_CHANGED,
                previous="None",
                current="BelarusPassport",
                created_at=datetime.datetime(2019, 8, 15, 10, 0),
                actor=ActorEnum.AUTOMATIC,
            ),
            DocumentLogEntityFactory(
                document_id=document1.pk,
                action=DocumentLogEnum.TYPE_CHANGED,
                previous="BelarusPassport",
                current="DirectionalSurvey",
                created_at=datetime.datetime(2019, 8, 15, 10, 30),
                actor=ActorEnum.MANUAL,
            ),
            DocumentLogEntityFactory(
                document_id=document2.pk,
                action=DocumentLogEnum.TYPE_CHANGED,
                previous="BelarusPassport",
                current="DirectionalSurvey",
                created_at=datetime.datetime(2019, 8, 15, 10, 55),
                actor=ActorEnum.MANUAL,
            ),
            DocumentLogEntityFactory(
                document_id=document2.pk,
                action=DocumentLogEnum.TYPE_CHANGED,
                previous="None",
                current="BelarusPassport",
                created_at=datetime.datetime(2019, 8, 15, 13, 5),
                actor=ActorEnum.AUTOMATIC,
            ),
        ]
        [uow.document_log().add(log_entity) for log_entity in document_log_entities]
