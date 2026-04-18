import pytest

from deps_documents.domain.exceptions import DocumentNotFoundError
from tests.factories import CommunicationEntityFactory, DocumentEntityFactory


class TestPartiallyUpdateDocumentUseCase:
    @pytest.mark.parametrize(
        "field,value",
        map(
            lambda field: (field, getattr(DocumentEntityFactory(communication=CommunicationEntityFactory(comments=[])), field)),
            (
                "title",
                "state",
                "files",
                "date",
                "document_type",
                "source_code",
                "reviewer",
                "language",
                "container_type",
                "container_metadata",
                "scraped_metadata",
                "preview_documents",
                "processing_documents",
                "error",
            ),
        ),
    )
    def test_partially_update__existing_document__update_fields(self, domain_services, uow, field, value):
        document = uow.document.add(DocumentEntityFactory())

        domain_services.document().partially_update(document.pk, {field: value})
        updated_document = uow.document.get(document.pk)

        assert getattr(updated_document, field) == value

    def test_partially_update__not_existing_doc__return_error(self, domain_services):
        with pytest.raises(DocumentNotFoundError):
            domain_services.document().partially_update("1", {"field": "value"})
