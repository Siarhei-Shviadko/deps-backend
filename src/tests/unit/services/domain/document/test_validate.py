import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.exceptions.document import DocumentValidationError
from tests.factories import DocumentEntityFactory


@pytest.mark.parametrize("state", DocumentStateEnum)
def test_validate__invalid_state__exception_raised(state, domain_services, uow):
    document = DocumentEntityFactory(state=state)
    uow.document.select_for_update.return_value = [document]
    allowed_states = {
        DocumentStateEnum.DATA_EXTRACTION,
        DocumentStateEnum.COMPLETED,
        DocumentStateEnum.FAILED,
        DocumentStateEnum.IN_REVIEW,
    }
    if state not in allowed_states:
        with pytest.raises(DocumentValidationError):
            domain_services.document().validate(document.pk)


def test_validate__validation_service_called(domain_services, uow, services):
    document = DocumentEntityFactory(state=DocumentStateEnum.COMPLETED)
    uow.document.select_for_update.return_value = [document]
    domain_services.document().validate(document)

    services.validation().send_document_to_validation.assert_called_with(document.pk)
