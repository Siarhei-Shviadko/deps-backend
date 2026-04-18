import uuid

from tests.factories import DocumentEntityFactory


class TestDocumentFileService:
    def test_execute__valid_data__return_document_id(self, domain_services, uow, services, blob_storage_mock):
        uow.document.add.return_value = DocumentEntityFactory(pk="1")

        result = domain_services.document().document_file(
            file_content=b"",
            file_name="file_name.pdf",
            document_name="document_name",
            source=None,
            run_pipeline=False,
            language="eng",
            engine="TESSERACT",
            llm_type=None,
            tenant=str(uuid.uuid4()),
            extraction_params={},
            reviewer=None,
        )

        assert result == "1"
