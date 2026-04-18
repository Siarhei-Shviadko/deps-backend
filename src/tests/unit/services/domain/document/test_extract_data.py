import pytest

from deps_documents.domain.exceptions import DocumentExtractDataError
from tests.factories import DocumentEntityFactory


class TestAssignTypeUseCase:
    def test_extract_data__document_data_error__raises_error(self, uow, domain_services):
        document = DocumentEntityFactory(pk=str(1), document_type="Unknown")

        uow.document.select_for_update.return_value = [document]

        with pytest.raises(DocumentExtractDataError):
            domain_services.document().extract_data(document.pk)
