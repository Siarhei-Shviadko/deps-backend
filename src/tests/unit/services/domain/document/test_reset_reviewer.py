import pytest

from deps_documents.domain.exceptions import DocumentReviewerError
from tests.factories import DocumentEntityFactory


class TestAssignTypeUseCase:
    def test_reset_reviewer__not_valid_reviewer__raises_error(self, uow, domain_services):
        document = DocumentEntityFactory(pk=str(1), reviewer=None)

        uow.document.select_for_update.return_value = [document]

        with pytest.raises(DocumentReviewerError):
            domain_services.document().reset_reviewer(document.pk)
