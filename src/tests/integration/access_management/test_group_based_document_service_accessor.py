import json
from http import HTTPStatus
from io import BytesIO

import pytest

from deps_documents.domain.constants import PipelineStepsEnum
from tests.factories.document_entity import (
    CommentEntityFactory,
    DocumentEntityFactory,
    DocumentFilesDataFactory,
    DocumentListDataFactory,
)
from tests.integration.access_management.conftest import TEST_DOCUMENT_PK
from tests.serializers import dump_document_for_request


@pytest.fixture
def dumped_document_request_data():
    document_dump = dump_document_for_request(DocumentEntityFactory(pk=TEST_DOCUMENT_PK))
    request_dump = {
        "document": {
            **document_dump,
        }
    }
    return json.dumps(request_dump)


@pytest.mark.usefixtures(
    "enable_authorization_for_services", "enable_group_based_access_management", "set_test_user", "document_fixture"
)
class TestGroupBasedDocumentServiceAccessor:
    documents_api = "/api/document/v1/documents"
    document_pk = TEST_DOCUMENT_PK
    comment = CommentEntityFactory()
    document_entity = DocumentEntityFactory(pk=document_pk)
    file_data = {
        "file": ("another_document_file.jpg", BytesIO(b"a new document file content"), "application/jpg"),
    }
    document_files = DocumentFilesDataFactory()
    document_list = DocumentListDataFactory()
    pipeline_params = {"documentIds": [document_pk], "engineName": "TESSERACT"}
    pipeline_from_step_params = {
        "documentIds": [document_pk],
        "step": PipelineStepsEnum.EXTRACTION,
        "engineName": "TESSERACT",
    }

    def test_add_comment__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.add_comment.return_value = self.comment
        response = client.post(f"{self.documents_api}/add-comment", json={"documentId": self.document_pk, "text": "comment"})

        assert response.status_code == HTTPStatus.OK

    def test_add_comment__user_has_no_access__forbidden(self, client, document_service_mock):
        document_service_mock.add_comment.return_value = self.comment
        response = client.post(f"{self.documents_api}/add-comment", json={"documentId": self.document_pk, "text": "comment"})

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_add_label__user_has_access_to_doc__org_has_access_to_label__success(
        self, client, document_service_mock, user_fixture, label_fixture, uow
    ):
        self._add_document_permission_to_user(uow, user_fixture)
        uow.label.add_label_to_organisation(label_fixture.pk, user_fixture["groups"][0])

        document_service_mock.add_label.return_value = [self.document_entity]
        response = client.post(
            f"{self.documents_api}/add-label", json={"documentIds": [self.document_pk], "labelId": label_fixture.pk}
        )

        assert response.status_code == HTTPStatus.OK

    def test_add_label__user_has_access_to_doc__org_has_no_access_to_label__forbidden(
        self, client, document_service_mock, uow, user_fixture, label_fixture
    ):
        self._add_document_permission_to_user(uow, user_fixture)

        document_service_mock.add_label.return_value = [self.document_entity]
        response = client.post(
            f"{self.documents_api}/add-label", json={"documentIds": [self.document_pk], "labelId": label_fixture.pk}
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_add_label__user_has_no_access_to_doc__org_has_access_to_label__forbidden(
        self, client, document_service_mock, user_fixture, label_fixture, uow
    ):
        uow.label.add_label_to_organisation(label_fixture.pk, user_fixture["groups"][0])

        document_service_mock.add_label.return_value = [self.document_entity]
        response = client.post(
            f"{self.documents_api}/add-label", json={"documentIds": [self.document_pk], "labelId": label_fixture.pk}
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_add_label__user_has_no_access_to_doc__org_has_no_access_to_label__forbidden(
        self, client, document_service_mock, label_fixture
    ):
        document_service_mock.add_label.return_value = [self.document_entity]
        response = client.post(
            f"{self.documents_api}/add-label", json={"documentIds": [self.document_pk], "labelId": label_fixture.pk}
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_assign_type__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.assign_type.return_value = [self.document_entity]
        response = client.post(
            f"{self.documents_api}/assign-type", json={"documentIds": [self.document_pk], "typeName": "Test type-code"}
        )

        assert response.status_code == HTTPStatus.OK

    def test_assign_type__user_has_no_access__forbidden(self, client, document_service_mock):
        document_service_mock.assign_type.return_value = [self.document_entity]
        response = client.post(
            f"{self.documents_api}/assign-type", json={"documentIds": [self.document_pk], "typeName": "Test type-code"}
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_complete_review__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.complete_review.return_value = self.document_entity
        response = client.post(f"{self.documents_api}/complete", json={"documentId": self.document_pk})

        assert response.status_code == HTTPStatus.OK

    def test_complete_review__user_has_no_access__forbidden(self, client, document_service_mock):
        document_service_mock.complete_review.return_value = self.document_entity
        response = client.post(f"{self.documents_api}/complete", json={"documentId": self.document_pk})

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_document_get__user_has_access__success(self, client, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        response = client.get(f"{self.documents_api}/{self.document_pk}")

        assert response.status_code == HTTPStatus.OK

    def test_document_get__user_has_no_access__forbidden(self, client):
        response = client.get(f"{self.documents_api}/{self.document_pk}")

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_document_put__user_has_access__success(self, client, uow, user_fixture, dumped_document_request_data):
        self._add_document_permission_to_user(uow, user_fixture)
        response = client.put(
            f"{self.documents_api}/{self.document_pk}",
            data=dumped_document_request_data,
        )

        assert response.status_code == HTTPStatus.OK

    def test_document_put__user_has_no_access__forbidden(self, client, dumped_document_request_data):
        response = client.put(
            f"{self.documents_api}/{self.document_pk}",
            data=dumped_document_request_data,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_document_patch__user_has_access__success(self, client, uow, user_fixture, dumped_document_request_data):
        self._add_document_permission_to_user(uow, user_fixture)
        response = client.patch(
            f"{self.documents_api}/{self.document_pk}",
            data=dumped_document_request_data,
        )

        assert response.status_code == HTTPStatus.OK

    def test_document_patch__user_has_no_access__forbidden(self, client, dumped_document_request_data):
        response = client.patch(
            f"{self.documents_api}/{self.document_pk}",
            data=dumped_document_request_data,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_document_delete__user_has_access__success(self, client, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        response = client.delete(f"{self.documents_api}/{self.document_pk}")

        assert response.status_code == HTTPStatus.OK

    def test_document_delete__user_has_no_access__forbidden(self, client):
        response = client.delete(f"{self.documents_api}/{self.document_pk}")

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_extract_data__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.extract_data.return_value = [self.document_entity]
        response = client.post(f"{self.documents_api}/extract-data", json={"documentIds": [self.document_pk]})

        assert response.status_code == HTTPStatus.OK

    def test_extract_data__user_has_no_access__forbidden(self, client, document_service_mock):
        document_service_mock.extract_data.return_value = [self.document_entity]
        response = client.post(f"{self.documents_api}/extract-data", json={"documentIds": [self.document_pk]})

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_document_file__document_added_to_user(self, client, document_service_mock):
        document_service_mock.document_file.return_value = self.document_pk
        document_service_mock.get.return_value = self.document_entity
        response = client.post(f"{self.documents_api}/document-file", files=self.file_data)
        assert response.status_code == HTTPStatus.OK

        document_pk = response.json()["id"]
        response = client.get(f"{self.documents_api}/{document_pk}")
        assert response.status_code == HTTPStatus.OK

    def test_files__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.get_document_files.return_value = self.document_files
        response = client.get(f"{self.documents_api}/{self.document_pk}/files")

        assert response.status_code == HTTPStatus.OK

    def test_files__user_has_no_access__forbidden(self, client, document_service_mock):
        document_service_mock.get_document_files.return_value = self.document_files
        response = client.get(f"{self.documents_api}/{self.document_pk}/files")

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_list__user_has_access__no_filter_applied(self, client, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        response = client.get(f"{self.documents_api}")
        document_list = response.json()

        assert response.status_code == HTTPStatus.OK
        assert document_list["meta"]["total"] == 1

    def test_list__user_has_no_access__document_filtered(self, client):
        response = client.get(f"{self.documents_api}")
        document_list = response.json()

        assert response.status_code == HTTPStatus.OK
        assert document_list["meta"]["total"] == 0

    def test_preprocessed_images__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.get_processed_images.return_value = self.document_files
        response = client.get(f"{self.documents_api}/{self.document_pk}/preprocessed-images")

        assert response.status_code == HTTPStatus.OK

    def test_preprocessed_images__user_has_no_access__success(self, client, document_service_mock):
        document_service_mock.get_processed_images.return_value = self.document_files
        response = client.get(f"{self.documents_api}/{self.document_pk}/preprocessed-images")

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_remove_label__user_has_access__success(self, client, document_service_mock, uow, user_fixture, label_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.remove_label.return_value = True
        response = client.post(
            f"{self.documents_api}/remove-label", json={"documentId": self.document_pk, "labelId": label_fixture.pk}
        )

        assert response.status_code == HTTPStatus.OK

    def test_remove_label__user_has_no_access__forbidden(self, client, document_service_mock, label_fixture):
        document_service_mock.remove_label.return_value = True
        response = client.post(
            f"{self.documents_api}/remove-label", json={"documentId": self.document_pk, "labelId": label_fixture.pk}
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_reset_reviewer__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.reset_reviewer.return_value = [self.document_entity]
        response = client.post(f"{self.documents_api}/reset-reviewer", json={"documentIds": [self.document_pk]})

        assert response.status_code == HTTPStatus.OK

    def test_reset_reviewer__user_has_no_access__forbidden(self, client, document_service_mock):
        document_service_mock.reset_reviewer.return_value = [self.document_entity]
        response = client.post(f"{self.documents_api}/reset-reviewer", json={"documentIds": [self.document_pk]})

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_retry_last_step__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.retry_last_step.return_value = self.document_entity
        response = client.post(f"{self.documents_api}/retry-last-step", json={"documentId": self.document_pk})

        assert response.status_code == HTTPStatus.OK

    def test_retry_last_step__user_has_no_access__forbidden(self, client, document_service_mock):
        document_service_mock.retry_last_step.return_value = self.document_entity
        response = client.post(f"{self.documents_api}/retry-last-step", json={"documentId": self.document_pk})

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_run_pipeline__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.run_pipeline.return_value = [self.document_entity]
        response = client.post(f"{self.documents_api}/run-pipeline", json=self.pipeline_params)

        assert response.status_code == HTTPStatus.OK

    def test_run_pipeline__user_has_no_access__forbidden(self, client, document_service_mock):
        document_service_mock.run_pipeline.return_value = [self.document_entity]
        response = client.post(f"{self.documents_api}/run-pipeline", json=self.pipeline_params)

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_run_pipeline_from_step__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.run_pipeline_from_step.return_value = [self.document_entity]
        response = client.post(
            f"{self.documents_api}/run-pipeline-from-step",
            json=self.pipeline_from_step_params,
        )

        assert response.status_code == HTTPStatus.OK

    def test_run_pipeline_from_step__user_has_no_access__forbidden(self, client, document_service_mock):
        document_service_mock.run_pipeline_from_step.return_value = [self.document_entity]
        response = client.post(
            f"{self.documents_api}/run-pipeline-from-step",
            json=self.pipeline_from_step_params,
        )

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_start_review__user_has_access__success(self, client, document_service_mock, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        document_service_mock.start_review.return_value = [self.document_entity]
        response = client.post(f"{self.documents_api}/start-review", json={"documentIds": [self.document_pk]})

        assert response.status_code == HTTPStatus.OK

    def test_start_review__user_has_no_access__forbidden(self, client, document_service_mock):
        document_service_mock.start_review.return_value = [self.document_entity]
        response = client.post(f"{self.documents_api}/start-review", json={"documentIds": [self.document_pk]})

        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_status__user_has_access__success(self, client, uow, user_fixture):
        self._add_document_permission_to_user(uow, user_fixture)
        response = client.get(f"{self.documents_api}/{self.document_pk}/status")

        assert response.status_code == HTTPStatus.OK

    def test_status__user_has_no_access__forbidden(self, client):
        response = client.get(f"{self.documents_api}/{self.document_pk}/status")

        assert response.status_code == HTTPStatus.FORBIDDEN

    def _add_document_permission_to_user(self, uow, user):
        uow.document.add_document_to_user(self.document_pk, user["subject"])
