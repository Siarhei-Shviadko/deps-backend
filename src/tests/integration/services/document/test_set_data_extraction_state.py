import pytest

from deps_documents.domain.constants import (
    DocumentExportTypesEnum,
    DocumentStateEnum,
    FieldTypeEnum,
)
from deps_documents.domain.exceptions import DocumentExtractDataError
from tests.factories import DocumentEntityFactory


class TestDocumentServiceSetDataExtractionState:
    @pytest.mark.skip
    def test_extract_data_unknown_type_of_document_raise_error(self, uow, domain_services):
        document_entity = uow.document.add(DocumentEntityFactory(document_type="test", title="Test doc.png"))

        with pytest.raises(DocumentExtractDataError):
            domain_services.document().extract_data([document_entity.pk])

    def test_extract_data_valid_type_of_document_changes_state(self, uow, domain_services):
        document_entity = uow.document.add(DocumentEntityFactory(document_type="test", title="Test doc.png"))
        response = domain_services.document().extract_data([document_entity.pk])
        assert response[0].state == DocumentStateEnum.DATA_EXTRACTION
