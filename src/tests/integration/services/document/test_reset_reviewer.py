import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.exceptions import DocumentReviewerError, PrimaryKeyError
from tests.factories import DocumentEntityFactory, ReviewerFactory


class TestDocumentServiceResetReviewer:
    def test_reset_reviewer__valid_document_pk__return_updated_doc(self, uow, domain_services):
        reviever = uow.document._save_reviewer(ReviewerFactory())
        document = uow.document.add(DocumentEntityFactory(reviewer=reviever))
        response = domain_services.document().reset_reviewer([document.pk])

        assert len(response) == 1

    def test_reset_reviewer__not_valid_reviewer__raise_error(self, uow, domain_services):
        document = uow.document.add(DocumentEntityFactory(reviewer=None))
        with pytest.raises(DocumentReviewerError):
            domain_services.document().reset_reviewer([document.pk])

    def test_reset_reviewer__not_valid_document_pk__raise_error(self, uow, domain_services):
        with pytest.raises(PrimaryKeyError):
            domain_services.document().reset_reviewer(["a"])

    def test_reset_reviewer__valid_reviewer__update_doc(self, uow, domain_services):
        reviever = uow.document._save_reviewer(ReviewerFactory())
        document = uow.document.add(DocumentEntityFactory(reviewer=reviever, state=DocumentStateEnum.NEW))
        domain_services.document().reset_reviewer([document.pk])

        updated_doc = uow.document.get(document.pk)

        assert updated_doc.state == DocumentStateEnum.COMPLETED
        assert updated_doc.reviewer is None
