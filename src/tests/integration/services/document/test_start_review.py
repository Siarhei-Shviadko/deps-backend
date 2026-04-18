import pytest

from deps_documents.domain.constants import START_REVIEW_STATES, DocumentStateEnum
from deps_documents.domain.exceptions import (
    DocumentAlreadyAssignedError,
    DocumentNotFoundError,
    DocumentReviewStateError,
    PrimaryKeyError,
)
from tests.factories import DocumentEntityFactory, ReviewerFactory


class TestDocumentServiceStartReview:
    def test_start_review__not_valid_document_pk__return_not_found_error(self, uow, domain_services):
        with pytest.raises(DocumentNotFoundError):
            domain_services.document().start_review(["1"])

    def test_start_review__not_valid_document_pks__return_pk_error(self, uow, domain_services):
        with pytest.raises(PrimaryKeyError):
            domain_services.document().start_review(["a"])

    @pytest.mark.parametrize("test_state,expected", [(state, state in START_REVIEW_STATES) for state in DocumentStateEnum])
    def test_start_review__valid_document_pk_different_states___update_doc_with_valid_state(
        self, test_state, expected, uow, domain_services
    ):
        document = uow.document.add(DocumentEntityFactory(state=test_state))
        if test_state not in START_REVIEW_STATES:
            with pytest.raises(DocumentReviewStateError):
                domain_services.document().start_review([document.pk])
        else:
            response = domain_services.document().start_review([document.pk])

            assert response[0].state == DocumentStateEnum.IN_REVIEW

    def test_start_review__document_not_assigned__set_reviewer(self, uow, domain_services):
        document = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED))

        reviewer = ReviewerFactory()
        documents = domain_services.document().start_review([document.pk], reviewer=reviewer, reassign_reviewer=True)

        assert documents[0].reviewer == reviewer
        assert documents[0].state == DocumentStateEnum.IN_REVIEW

    def test_start_review__document_not_assigned__reviewer_reassign_disabled(self, uow, domain_services):
        document = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED))

        reviewer = ReviewerFactory()
        documents = domain_services.document().start_review([document.pk], reviewer=reviewer, reassign_reviewer=False)

        assert documents[0].reviewer is None
        assert documents[0].state == DocumentStateEnum.IN_REVIEW

    def test_start_review__document_assigned_to_same_user__set_reviewer(self, uow, domain_services):
        reviewer = ReviewerFactory()
        document = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED, reviewer=reviewer))

        documents = domain_services.document().start_review([document.pk], reviewer=reviewer, reassign_reviewer=True)

        assert documents[0].reviewer == reviewer
        assert documents[0].state == DocumentStateEnum.IN_REVIEW

    def test_start_review__document_assigned_to_same_user__reviewer_reassign_disabled(self, uow, domain_services):
        reviewer = ReviewerFactory()
        document = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED, reviewer=reviewer))

        documents = domain_services.document().start_review([document.pk], reviewer=reviewer, reassign_reviewer=False)

        assert documents[0].reviewer == reviewer
        assert documents[0].state == DocumentStateEnum.IN_REVIEW

    def test_start_review__document_already_assigned__raise_error(self, uow, domain_services):
        document = uow.document.add(
            DocumentEntityFactory(
                state=DocumentStateEnum.COMPLETED,
                reviewer=ReviewerFactory(),
            )
        )

        reviewer = ReviewerFactory()
        with pytest.raises(DocumentAlreadyAssignedError):
            domain_services.document().start_review([document.pk], reviewer=reviewer, reassign_reviewer=True)

    def test_start_review__document_already_assigned__reviewer_reassign_disabled(self, uow, domain_services):
        reviewer = ReviewerFactory()
        document = uow.document.add(
            DocumentEntityFactory(
                state=DocumentStateEnum.COMPLETED,
                reviewer=reviewer,
            )
        )

        documents = domain_services.document().start_review([document.pk], reviewer=ReviewerFactory(), reassign_reviewer=False)

        assert documents[0].reviewer == reviewer
        assert documents[0].state == DocumentStateEnum.IN_REVIEW
