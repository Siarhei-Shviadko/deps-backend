from operator import itemgetter

import pytest

from deps_documents.domain.constants import DocumentStateEnum
from tests.factories import DocumentEntityFactory, ReviewerFactory


class TestDocumentStartReviewIntegrity:
    def test_request__valid_data__valid_response(self, client, uow):
        document1 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED))

        expected_updated_documents = set([document1.pk])

        response = client.post(
            "/api/document/v1/documents/start-review",
            json={
                "documentIds": [document1.pk],
            },
        )

        response = response.json()
        actual_updated_documents = set(map(itemgetter("_id"), response))

        assert actual_updated_documents == expected_updated_documents

    def test_post__document_not_in_completed_state__return_400(self, client, uow):
        document1 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.NEW))

        response = client.post(
            "/api/document/v1/documents/start-review",
            json={
                "documentIds": [document1.pk],
            },
        )

        assert response.status_code == 400

    @pytest.mark.usefixtures("set_test_user")
    def test_post__document_not_assigned__return_200(self, client, uow, user_fixture, enable_reviewer_reassign):
        document1 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED))

        response = client.post(
            "/api/document/v1/documents/start-review",
            json={
                "documentIds": [document1.pk],
            },
        )

        resp_json = response.json()

        assert response.status_code == 200
        assert resp_json[0]["reviewer"] is not None
        assert resp_json[0]["reviewer"]["id"] == user_fixture["subject"]
        assert resp_json[0]["state"] == DocumentStateEnum.IN_REVIEW

    @pytest.mark.usefixtures("set_test_user")
    def test_post__document_not_assigned__reviewer_reassign_disabled__return_200(self, client, uow, user_fixture):
        document1 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED))

        response = client.post(
            "/api/document/v1/documents/start-review",
            json={
                "documentIds": [document1.pk],
            },
        )

        resp_json = response.json()

        assert response.status_code == 200
        assert resp_json[0]["reviewer"] is None
        assert resp_json[0]["state"] == DocumentStateEnum.IN_REVIEW

    @pytest.mark.usefixtures("set_test_user")
    def test_post__document_assigned_to_same_user__return_200(self, client, uow, user_fixture, enable_reviewer_reassign):
        reviewer = ReviewerFactory(
            id=user_fixture["subject"],
            email=user_fixture["email"],
            first_name=user_fixture["first_name"],
            last_name=user_fixture["last_name"],
        )
        document1 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED, reviewer=reviewer))

        response = client.post(
            "/api/document/v1/documents/start-review",
            json={
                "documentIds": [document1.pk],
            },
        )

        resp_json = response.json()

        assert response.status_code == 200
        assert resp_json[0]["reviewer"] is not None
        assert resp_json[0]["reviewer"]["id"] == user_fixture["subject"]
        assert resp_json[0]["state"] == DocumentStateEnum.IN_REVIEW

    @pytest.mark.usefixtures("set_test_user")
    def test_post__document_assigned_to_same_user__reviewer_reassign_disabled__return_200(self, client, uow, user_fixture):
        reviewer = ReviewerFactory(
            id=user_fixture["subject"],
            email=user_fixture["email"],
            first_name=user_fixture["first_name"],
            last_name=user_fixture["last_name"],
        )
        document1 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED, reviewer=reviewer))

        response = client.post(
            "/api/document/v1/documents/start-review",
            json={
                "documentIds": [document1.pk],
            },
        )

        resp_json = response.json()

        assert response.status_code == 200
        assert resp_json[0]["reviewer"] is not None
        assert resp_json[0]["reviewer"]["id"] == user_fixture["subject"]
        assert resp_json[0]["state"] == DocumentStateEnum.IN_REVIEW

    @pytest.mark.usefixtures("set_test_user")
    def test_post__document_already_assigned__return_400(self, client, uow, user_fixture, enable_reviewer_reassign):
        reviewer = ReviewerFactory()
        document1 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED, reviewer=reviewer))

        response = client.post(
            "/api/document/v1/documents/start-review",
            json={
                "documentIds": [document1.pk],
            },
        )

        assert response.status_code == 400

    @pytest.mark.usefixtures("set_test_user")
    def test_post__document_already_assigned__reviewer_reassign_disabled__return_200(self, client, uow, user_fixture):
        reviewer = ReviewerFactory()
        document1 = uow.document.add(DocumentEntityFactory(state=DocumentStateEnum.COMPLETED, reviewer=reviewer))

        response = client.post(
            "/api/document/v1/documents/start-review",
            json={
                "documentIds": [document1.pk],
            },
        )

        resp_json = response.json()

        assert response.status_code == 200
        assert resp_json[0]["state"] == DocumentStateEnum.IN_REVIEW
