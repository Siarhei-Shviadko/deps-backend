from copy import deepcopy

import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.infrastructure.services import CorleoneService, ValidationService
from tests.factories import DocumentEntityFactory


@pytest.fixture(scope="function", autouse=True)
def validation_service(mocker, services):
    validation_service_mock = mocker.Mock(ValidationService)

    with services.validation.override(validation_service_mock):
        yield validation_service_mock
    services.validation.reset_override()


@pytest.fixture(scope="function", autouse=True)
def corleone_service(mocker, services):
    corleone_service_mock = mocker.Mock(CorleoneService)

    with services.corleone_service.override(corleone_service_mock):
        yield corleone_service_mock
    services.corleone_service.reset_override()


class TestDocumentCompleteIntegrity:
    def test_request__valid_data__valid_response(self, client, uow, services, corleone_service):
        document = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.IN_REVIEW))
        corleone_service.is_extracted_data_exists.return_value = True

        response = client.post("/api/document/v1/documents/complete", json={"documentId": document.pk})

        json_response = response.json()

        expected = deepcopy(document)
        expected.state = DocumentStateEnum.VALIDATION

        assert json_response.get("_id") == expected.pk
        assert json_response.get("parentId") == expected.parent_id
        assert json_response.get("title") == expected.title
        assert json_response.get("state") == expected.state
        assert json_response.get("documentType") == expected.document_type
        assert json_response.get("date") == expected.date.isoformat()
        assert json_response.get("reviewer") == expected.reviewer
        assert isinstance(json_response.get("labels"), list)
        assert len(json_response.get("labels")) == len(expected.labels)
        assert json_response.get("language") == expected.language
        assert json_response.get("engine") == expected.engine
        assert isinstance(json_response.get("previewDocuments"), dict)
        assert isinstance(json_response.get("processingDocuments"), dict)
        assert json_response.get("priority") == expected.priority.value

    def test_request__valid_data__no_extracted_data__validation_rejected(self, client, uow, services, corleone_service):
        document = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.IN_REVIEW))
        corleone_service.is_extracted_data_exists.return_value = False

        response = client.post("/api/document/v1/documents/complete", json={"documentId": document.pk})

        json_response = response.json()

        assert json_response.get("state") == DocumentStateEnum.COMPLETED
