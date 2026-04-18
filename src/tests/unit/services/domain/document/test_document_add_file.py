import pytest

from deps_documents.domain.exceptions import DocumentNotFoundError
from tests.factories import DocumentEntityFactory


class TestDocumentAddFileUseCase:
    def test_execute__valid_data__return_document_id(self, domain_services, uow, services, blob_storage_mock):
        uow.document.update.return_value = DocumentEntityFactory(pk="1")

        result = domain_services.document().add_file(
            "1",
            file_content=b"",
            file_name="file_name",
        )

        assert result == "1"

    def test_execute__not_exiting_document__return_error(self, domain_services, uow, services, blob_storage_mock):
        uow.document.select_for_update.side_effect = DocumentNotFoundError

        with pytest.raises(DocumentNotFoundError):
            domain_services.document().add_file(
                "1",
                file_content=b"",
                file_name="file_name",
            )
