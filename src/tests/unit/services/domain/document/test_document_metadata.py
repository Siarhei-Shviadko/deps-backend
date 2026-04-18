from deps_documents.domain.entities import DocumentMetadata


class TestDocumentMetadata:
    def test_upsert_document_metadata(self, domain_services, uow, document_metadata):
        uow.document.upsert_document_metadata.return_value = document_metadata
        added_metadata = domain_services.document().upsert_document_metadata(document_metadata)

        assert isinstance(added_metadata, DocumentMetadata)
        assert added_metadata == document_metadata

    def test_get_document_metadata(self, domain_services, uow, document_metadata):
        uow.document.get_document_metadata.return_value = document_metadata
        metadata = domain_services.document().get_document_metadata(document_metadata.document_id)

        assert isinstance(metadata, DocumentMetadata)
        assert metadata == document_metadata

    def test_delete_document_metadata(self, domain_services, uow, document_metadata):
        uow.document.delete_document_metadata.return_value = None
        domain_services.document().delete_document_metadata(document_metadata)
