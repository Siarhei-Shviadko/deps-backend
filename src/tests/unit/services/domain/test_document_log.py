from datetime import datetime, timedelta

import pytest

from deps_documents.domain.constants import DocumentLogEnum, DocumentStateEnum
from deps_documents.domain.entities import DocumentEntity, DocumentLogEntity
from deps_documents.domain.exceptions import DocumentNotFoundError
from tests.factories import DocumentEntityFactory


@pytest.fixture
def domain_services(domain_services):
    domain_services.document_log.reset_override()

    return domain_services


class TestDocumentFileService:
    def test_retrieve_state_intervals__existing_document(self, domain_services, uow):
        uow.document.get.return_value = DocumentEntityFactory(date=datetime.now())
        uow.document_log.get_document_logs.return_value = [
            DocumentLogEntity(
                action=DocumentLogEnum.STATE_CHANGED,
                previous=str(DocumentStateEnum.PREPROCESSING),
                current=str(DocumentStateEnum.DATA_EXTRACTION),
                created_at=datetime.now(),
                document_id="1",
            ),
            DocumentLogEntity(
                action=DocumentLogEnum.STATE_CHANGED,
                previous=str(DocumentStateEnum.DATA_EXTRACTION),
                current=str(DocumentStateEnum.IN_REVIEW),
                created_at=datetime.now(),
                document_id="1",
            ),
            DocumentLogEntity(
                action=DocumentLogEnum.TYPE_CHANGED,
                previous="preview value",
                current="current value",
                created_at=datetime.now(),
                document_id="1",
            ),
            DocumentLogEntity(
                action=DocumentLogEnum.TYPE_CHANGED,
                previous="current value",
                current="yet another current value",
                created_at=datetime.now(),
                document_id="1",
            ),
            DocumentLogEntity(
                action=DocumentLogEnum.STATE_CHANGED,
                previous=str(DocumentStateEnum.NEW),
                current=str(DocumentStateEnum.PREPROCESSING),
                created_at=datetime.now() - timedelta(hours=1),
                document_id="1",
            ),
        ]

        result = domain_services.document_log().get_document_time_state_intervals(document_id="1")

        uow.document_log.get_document_logs.assert_called_with("1")
        assert len(result) == 4
        assert result[0].start_time < result[-1].finish_time
        assert result[0].state == DocumentStateEnum.NEW
        assert result[1].state == DocumentStateEnum.PREPROCESSING
        assert result[-1].state == DocumentStateEnum.IN_REVIEW

    def test_retrieve_state_intervals__not_existing_file__raise_not_found(self, domain_services, uow):
        uow.document_log.get_document_logs.side_effect = DocumentNotFoundError

        with pytest.raises(DocumentNotFoundError):
            domain_services.document_log().get_document_time_state_intervals(document_id="1")
