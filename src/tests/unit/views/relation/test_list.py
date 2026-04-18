from dataclasses import asdict
from http import HTTPStatus

import pytest

from deps_documents.domain.entities import RelationEntity
from deps_documents.domain.exceptions import (
    RelationAlreadyExistsError,
    RelationNotFoundError,
    RelationTypeNotFoundError,
)

from .conftest import RELATION_ENDPOINT

TEST_TYPE = "testType"
TEST_CODE = "testCode"
LIST_TYPE_ENDPOINT = f"{RELATION_ENDPOINT}/{TEST_TYPE}"
DETAIL_ENDPOINT = f"{LIST_TYPE_ENDPOINT}/{TEST_CODE}"
RELATION_ENDPOINT = f"{RELATION_ENDPOINT}/"


@pytest.mark.parametrize("endpoint", (RELATION_ENDPOINT, DETAIL_ENDPOINT))
def test_get__return_200(client, relation_service_mock, relation_mock_list, endpoint):
    relation_service_mock.get_relation_list.return_value = relation_mock_list
    response = client.get(endpoint)
    assert response.status_code == HTTPStatus.OK

    response_content = response.json()
    assert response_content["meta"]["total"] == relation_mock_list.meta.total
    assert response_content["meta"]["size"] == relation_mock_list.meta.size
    assert len(response_content["result"]) == len(relation_mock_list.content)


@pytest.mark.parametrize("endpoint", (RELATION_ENDPOINT, DETAIL_ENDPOINT))
def test_get__no_relation__return_404(client, relation_service_mock, relation_mock, endpoint):
    relation_service_mock.get_relation_list.side_effect = RelationNotFoundError(relation_mock)
    response = client.get(endpoint)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_post__empty_url_valid_body_data__return_200(client, relation_service_mock, relation_post_body_mock, relation_mock):
    relation_service_mock.create_relation.return_value = relation_mock

    response = client.post(RELATION_ENDPOINT, json=relation_post_body_mock)

    called_relation = RelationEntity(
        type=relation_post_body_mock["type"],
        code=relation_post_body_mock["code"],
        assigned_documents=relation_post_body_mock["assignedDocuments"],
    )
    assert response.status_code == HTTPStatus.CREATED
    relation_service_mock.create_relation.assert_called_with(called_relation)


def test_post__url_type_code_valid_body_data__return_201(client, relation_service_mock, relation_post_body_mock, relation_mock):
    relation_service_mock.create_relation.return_value = relation_mock

    relation_post_body_mock.pop("type")
    relation_post_body_mock.pop("code")
    response = client.post(DETAIL_ENDPOINT, json=relation_post_body_mock)

    called_relation = RelationEntity(
        type=TEST_TYPE, code=TEST_CODE, assigned_documents=relation_post_body_mock["assignedDocuments"]
    )
    assert response.status_code == HTTPStatus.CREATED
    relation_service_mock.create_relation.assert_called_with(called_relation)


@pytest.mark.parametrize(
    "missed",
    (
        {"endpoint": RELATION_ENDPOINT, "arg": "code"},
        {"endpoint": RELATION_ENDPOINT, "arg": "type"},
    ),
)
def test_post__no_relation_type__return_422(client, relation_service_mock, relation_post_body_mock, relation_mock, missed):
    relation_service_mock.create_relation.return_value = relation_mock

    relation_post_body_mock.pop(missed["arg"])

    response = client.post(missed["endpoint"], json=relation_post_body_mock)

    assert response.status_code == 422


def test_post__incorrect_assigned_documents__return_422(client, relation_service_mock, relation_mock, relation_post_body_mock):
    relation_service_mock.create_relation.return_value = relation_mock
    relation_post_body_mock["assignedDocuments"] = 1

    response = client.post(RELATION_ENDPOINT, json=relation_post_body_mock)

    assert response.status_code == 422


def test_post__relation_already_exist__return_400(client, relation_service_mock, relation_post_body_mock, relation_mock):
    relation_service_mock.create_relation.side_effect = RelationAlreadyExistsError(relation_mock)
    request_json = relation_post_body_mock
    response = client.post(RELATION_ENDPOINT, json=request_json)

    assert response.status_code == 409


def test_post__relation_type_does_not_exist__return_404(client, relation_service_mock, relation_post_body_mock, relation_mock):
    relation_service_mock.create_relation.side_effect = RelationTypeNotFoundError(relation_mock.type)
    request_json = relation_post_body_mock
    response = client.post(RELATION_ENDPOINT, json=request_json)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("list_endpoint", (DETAIL_ENDPOINT,))
def test_list_by_type__return_200(client, relation_service_mock, relation_mock_list, list_endpoint):
    relation_service_mock.get_relation_list.return_value = relation_mock_list
    response = client.get(list_endpoint)
    assert response.status_code == HTTPStatus.OK

    response_content = response.json()
    assert response_content["meta"]["total"] == relation_mock_list.meta.total
    assert response_content["meta"]["size"] == relation_mock_list.meta.size
    assert len(response_content["result"]) == len(relation_mock_list.content)


def test_put__return_200(client, relation_service_mock, relation_mock, relation_put_body_mock):
    relation_service_mock.update.return_value = relation_mock

    response = client.put(DETAIL_ENDPOINT, json=relation_put_body_mock)

    assert response.status_code == HTTPStatus.OK
    content = response.json()

    assert relation_mock.assigned_documents == content["assignedDocuments"]
    assert relation_mock.parent_code == content["parentCode"]
    assert relation_mock.parent_type == content["parentType"]


@pytest.mark.parametrize("delete_field", ("type", "code"))
def test_put__correct_schema_deleted_field__return_400(
    client, relation_service_mock, relation_mock, relation_put_body_mock, delete_field
):
    relation_service_mock.update.return_value = relation_mock

    relation_put_body_mock.pop(delete_field)
    response = client.put(DETAIL_ENDPOINT, json=relation_put_body_mock)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("empty_field", ("type", "code"))
def test_put__incorrect_schema__return_422(client, relation_service_mock, relation_mock, relation_put_body_mock, empty_field):
    relation_service_mock.update.return_value = relation_mock

    relation_put_body_mock[empty_field] = ""
    response = client.put(DETAIL_ENDPOINT, json=relation_put_body_mock)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_delete__return_200(client, relation_service_mock):
    relation_service_mock.delete_relation.return_value = True

    response = client.delete(DETAIL_ENDPOINT)

    assert response.status_code == HTTPStatus.OK
    assert response.json()["deleted"]


def test_delete__relation_doesnt_exist__return_400(client, relation_service_mock, relation_mock):
    relation_service_mock.delete_relation.side_effect = RelationNotFoundError(relation_mock)

    response = client.delete(DETAIL_ENDPOINT)

    assert response.status_code == HTTPStatus.NOT_FOUND
