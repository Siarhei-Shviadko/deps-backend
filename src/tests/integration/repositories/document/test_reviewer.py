import pytest

from deps_documents.domain.exceptions import ReviewerNotFoundError
from tests.factories import ReviewerFactory


class TestDocumentEntityRepositoryGetReviewer:
    def test_get_reviewer__reviewer_exists(self, uow):
        reviewer = ReviewerFactory()
        uow.document._save_reviewer(reviewer)

        result = uow.document._find_reviewer(reviewer.id)

        assert result.id == reviewer.id

    def test_get_reviewer__reviewer_not_found(self, uow):
        with pytest.raises(ReviewerNotFoundError):
            uow.document._find_reviewer("non_existing_id")

    def test_create_reviewer__return_reviewer(self, uow):
        reviewer = ReviewerFactory()
        result = uow.document._save_reviewer(reviewer)

        assert all(
            (
                reviewer.id == result.id,
                reviewer.email == result.email,
                reviewer.first_name == result.first_name,
                reviewer.last_name == result.last_name,
            )
        )
