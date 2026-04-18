import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.entities import DocumentMetadata
from deps_documents.domain.events import DocumentStateUpdated
from deps_documents.domain.exceptions import (
    DocumentAlreadyAssignedError,
    DocumentReviewStateError,
)
from tests.factories import DocumentEntityFactory, ReviewerFactory


class TestAssignTypeUseCase:
    def test_start_review__document_wrong_state__raises_error(self, uow, domain_services):
        document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.DATA_EXTRACTION)

        uow.document.select_for_update.return_value = [document]

        with pytest.raises(DocumentReviewStateError):
            domain_services.document().start_review(document.pk)

    def test_start_review__document_not_assigned__return_document(self, uow, domain_services):
        document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.COMPLETED)

        uow.document.select_for_update.return_value = [document]
        uow.document.batch_update.return_value = [document]

        reviewer = ReviewerFactory()
        documents = domain_services.document().start_review(document.pk, reviewer=reviewer, reassign_reviewer=True)

        assert documents[0].reviewer == reviewer
        assert documents[0].state == DocumentStateEnum.IN_REVIEW

    def test_start_review__document_not_assigned__reviewer_reassign_disabled__return_document(self, uow, domain_services):
        document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.COMPLETED)

        uow.document.select_for_update.return_value = [document]
        uow.document.batch_update.return_value = [document]

        reviewer = ReviewerFactory()
        documents = domain_services.document().start_review(document.pk, reviewer=reviewer)

        assert documents[0].reviewer is None
        assert documents[0].state == DocumentStateEnum.IN_REVIEW

    def test_start_review__document_assign_same_user__return_document(self, uow, domain_services):
        reviewer = ReviewerFactory()
        document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.COMPLETED, reviewer=reviewer)

        uow.document.select_for_update.return_value = [document]
        uow.document.batch_update.return_value = [document]

        documents = domain_services.document().start_review(document.pk, reviewer=reviewer, reassign_reviewer=True)

        assert documents[0].reviewer == reviewer
        assert documents[0].state == DocumentStateEnum.IN_REVIEW

    def test_start_review__document_assign_same_user__reviewer_reassign_disabled__return_document(self, uow, domain_services):
        reviewer = ReviewerFactory()
        document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.COMPLETED, reviewer=reviewer)

        uow.document.select_for_update.return_value = [document]
        uow.document.batch_update.return_value = [document]

        documents = domain_services.document().start_review(document.pk, reviewer=reviewer)

        assert documents[0].reviewer == reviewer
        assert documents[0].state == DocumentStateEnum.IN_REVIEW

    def test_start_review__document_already_assigned__raises_error(self, uow, domain_services):
        document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.COMPLETED, reviewer=ReviewerFactory())

        uow.document.select_for_update.return_value = [document]
        uow.document.batch_update.return_value = [document]

        with pytest.raises(DocumentAlreadyAssignedError):
            domain_services.document().start_review(document.pk, reviewer=ReviewerFactory(), reassign_reviewer=True)

    def test_start_review__document_already_assigned__reviewer_reassign_disabled__return_document(self, uow, domain_services):
        reviewer = ReviewerFactory()
        document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.COMPLETED, reviewer=reviewer)

        uow.document.select_for_update.return_value = [document]
        uow.document.batch_update.return_value = [document]

        documents = domain_services.document().start_review(document.pk, reviewer=ReviewerFactory())

        assert documents[0].reviewer == reviewer
        assert documents[0].state == DocumentStateEnum.IN_REVIEW

    def test_start_review__events_sent(self, uow, domain_services):
        document = DocumentEntityFactory(pk=str(1), state=DocumentStateEnum.COMPLETED)
        uow.document.select_for_update.return_value = [document]
        uow.document.batch_update.return_value = [document]
        uow.document.get_document_metadata.return_value = DocumentMetadata(document.pk)

        domain_services.document().start_review(document.pk)

        uow.add_events.assert_called_once_with(
            [DocumentStateUpdated(document_id=document.pk, state=DocumentStateEnum.IN_REVIEW.value, metadata={})],
        )
