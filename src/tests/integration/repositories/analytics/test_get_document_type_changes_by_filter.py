import datetime

from deps_documents.domain.constants import ActorEnum, DocumentLogEnum, TimePeriodEnum
from deps_documents.domain.dtos import DateTimeRangeObject, DocumentTypeChangeFilter
from tests.factories import DocumentEntityFactory, DocumentLogEntityFactory


class TestCaseDocumentLogEntityRepositoryGetDocumentTypeChanges:
    def test_aggregate_by_filter__no_params__return_all_data_by_hour(self, uow):
        self._create_data(uow)
        result = uow.analytics.get_document_type_changes(DocumentTypeChangeFilter())
        assert len(result) == 3

    def test_aggregate_by_filter__aggregate_by_hour__return_all_data_by_hour(self, uow):
        self._create_data(uow)
        result = uow.analytics.get_document_type_changes(DocumentTypeChangeFilter(aggregation_period=TimePeriodEnum.HOUR))
        assert len(result) == 3

    def test_aggregate_by_filter__aggregate_by_day__return_all_data_by_day(self, uow):
        self._create_data(uow)
        result = uow.analytics.get_document_type_changes(DocumentTypeChangeFilter(aggregation_period=TimePeriodEnum.DAY))
        assert len(result) == 2

    def test_aggregate_by_filter__previous__return_data(self, uow):
        self._create_data(uow)
        result = uow.analytics.get_document_type_changes(DocumentTypeChangeFilter(old_type="None"))
        assert len(result) == 2

    def test_aggregate_by_filter__current__return_data(self, uow):
        self._create_data(uow)
        result = uow.analytics.get_document_type_changes(DocumentTypeChangeFilter(new_type="BelarusPassport"))
        assert len(result) == 2

    def test_aggregate_by_filter__date_range__return_data(self, uow):
        self._create_data(uow)
        date_range = DateTimeRangeObject(start=datetime.datetime(2019, 8, 15, 8, 0), end=datetime.datetime(2019, 8, 15, 10, 31))
        result = uow.analytics.get_document_type_changes(DocumentTypeChangeFilter(date_range=date_range))
        assert len(result) == 2

    def test_aggregate_by_filter__actor__return_data(self, uow):
        self._create_data(uow)
        result = uow.analytics.get_document_type_changes(DocumentTypeChangeFilter(changed_by="manual"))
        assert len(result) == 1

    def test_aggregate_by_filter__all_filter_fields__return_data(self, uow):
        self._create_data(uow)
        date_range = DateTimeRangeObject(start=datetime.datetime(2019, 8, 15, 8, 0), end=datetime.datetime(2019, 8, 15, 10, 31))
        result = uow.analytics.get_document_type_changes(
            DocumentTypeChangeFilter(old_type="None", new_type="BelarusPassport", date_range=date_range, changed_by="automatic")
        )
        assert len(result) == 1

    def test_aggregate_by_filter__filter__return_no_data(self, uow):
        self._create_data(uow)
        result = uow.analytics.get_document_type_changes(DocumentTypeChangeFilter(old_type="None", new_type="DirectionalSurvey"))
        assert len(result) == 0

    def _create_data(self, uow):
        document1 = uow.document.add(DocumentEntityFactory())
        document2 = uow.document.add(DocumentEntityFactory())

        # log entries 1 and 2 are the same within the same hour so they should grouped into one by SQL query
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
        [uow.document_log.add(log_entity) for log_entity in document_log_entities]
