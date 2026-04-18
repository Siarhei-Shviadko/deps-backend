from http import HTTPStatus

import pytest

from deps_documents.domain.constants import AssignAction
from deps_documents.domain.exceptions import (
    AssignedDocumentDeletingError,
    DocumentAlreadyAssignedError,
    DocumentAssigningError,
    RelationNotFoundError,
)
from tests.factories import RelationEntityFactory

from .conftest import assign_patch_generate_invalid_body_generator
from .test_list import DETAIL_ENDPOINT

ASSIGN_ENDPOINT = f"{DETAIL_ENDPOINT}/assign"


def test_assign_post__valid_data__return_201(client, relation_service_mock):
    relation_service_mock.assign_document.return_value = None

    json_body = {"assignedDocuments": [1, 2, 3]}
    response = client.post(ASSIGN_ENDPOINT, json=json_body)

    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.parametrize("doc_body", ("0", None, {"foo": "boo"}))
def test_assign_post__invalid_data__return_422(client, relation_service_mock, doc_body):
    relation_service_mock.assign_document.return_value = None

    json_body = {"assignedDDocuments": doc_body}
    response = client.post(ASSIGN_ENDPOINT, json=json_body)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_assign_post__validation__return_422(client, relation_service_mock):
    relation_service_mock.assign_document.return_value = None

    json_body = {}
    response = client.post(ASSIGN_ENDPOINT, json=json_body)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_assign_post__doc_or_relation_does_not_exist__return_404(client, relation_service_mock, assign_post_body_mock):
    relation_service_mock.assign_document.side_effect = (RelationNotFoundError(RelationEntityFactory()),)
    response = client.post(ASSIGN_ENDPOINT, json=assign_post_body_mock)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "assign_exception",
    (
        DocumentAssigningError(RelationEntityFactory().assigned_documents),
        DocumentAlreadyAssignedError(RelationEntityFactory().assigned_documents),
    ),
)
def test_assign_post__already_assigned__return_400(client, relation_service_mock, assign_post_body_mock, assign_exception):
    relation_service_mock.assign_document.side_effect = assign_exception

    response = client.post(ASSIGN_ENDPOINT, json=assign_post_body_mock)

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_assign_delete__return_200(client, relation_service_mock):
    relation_service_mock.delete_assigned_documents.return_value = True
    response = client.delete(ASSIGN_ENDPOINT)

    assert response.status_code == HTTPStatus.OK


def test_assign_delete__not_found_relation__return_404(client, relation_service_mock):
    relation_service_mock.delete_assigned_documents.side_effect = RelationNotFoundError(RelationEntityFactory())
    response = client.delete(ASSIGN_ENDPOINT)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_assign_patch__add__return_200(client, relation_service_mock, assign_patch_body_mock):
    assign_patch_body_mock["action"] = AssignAction.ADD.value
    relation_service_mock.assign_document.return_value = None
    response = client.patch(ASSIGN_ENDPOINT, json=assign_patch_body_mock)

    assert response.status_code == HTTPStatus.CREATED


def test_assign_patch__delete__return_201(client, relation_service_mock, assign_patch_body_mock):
    assign_patch_body_mock["action"] = AssignAction.DELETE.value
    relation_service_mock.delete_assigned_documents.return_value = True
    response = client.patch(ASSIGN_ENDPOINT, json=assign_patch_body_mock)

    assert response.status_code == HTTPStatus.CREATED


@pytest.mark.parametrize("json_body", assign_patch_generate_invalid_body_generator())
def test_assign_patch__invalid_body__return_422(client, relation_service_mock, json_body):
    relation_service_mock.delete_assigned_documents.return_value = True
    response = client.patch(ASSIGN_ENDPOINT, json=json_body)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("assign_exception", (DocumentAssigningError,))
def test_assign_patch_add__raise_exception__return_400(client, relation_service_mock, assign_exception, assign_patch_body_mock):
    assign_patch_body_mock["action"] = AssignAction.ADD.value

    relation_service_mock.assign_document.side_effect = assign_exception
    response = client.patch(ASSIGN_ENDPOINT, json=assign_patch_body_mock)

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_assign_patch_delete__raise_exception__return_400(client, relation_service_mock, assign_patch_body_mock):
    assign_patch_body_mock["action"] = AssignAction.DELETE.value

    relation_service_mock.delete_assigned_documents.side_effect = AssignedDocumentDeletingError
    response = client.patch(ASSIGN_ENDPOINT, json=assign_patch_body_mock)

    assert response.status_code == HTTPStatus.BAD_REQUEST
