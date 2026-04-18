from http import HTTPStatus

from deps_documents.domain.dtos import (
    ListResponseMetaDataObject,
    RelationTypeDataObject,
)
from deps_documents.domain.entities import RelationType

from .conftest import RELATION_ENDPOINT

TYPE_LIST_ENDPOINT = f"{RELATION_ENDPOINT}/types"
DETAIL_ENDPOINT = f"{TYPE_LIST_ENDPOINT}/some_type"


def test_list__return_200(client, relation_service_mock, type_list_mock):
    relation_service_mock.get_relation_type_list.return_value = RelationTypeDataObject(
        meta=ListResponseMetaDataObject(
            total=type_list_mock.get("meta", {}).get("total", 1),
            size=type_list_mock.get("meta", {}).get("size", 1),
        ),
        content=[RelationType(rel_type) for rel_type in type_list_mock.get("content")],
    )
    response = client.get(TYPE_LIST_ENDPOINT)
    assert response.status_code == HTTPStatus.OK

    content = response.json()
    assert content["meta"]["total"] == type_list_mock["meta"]["total"]
    assert content["meta"]["size"] == type_list_mock["meta"]["size"]
    assert len(content["result"]) == len(type_list_mock["content"])


def test_post__valid_data__return_201(client, relation_service_mock, relation_type_mock):
    relation_service_mock.create_relation_type.return_value = relation_type_mock
    request_json = {"type": "testType1"}

    response = client.post(TYPE_LIST_ENDPOINT, json=request_json)

    assert response.status_code == HTTPStatus.CREATED


def test_post__no_type__return_422(client, relation_service_mock, relation_type_mock):
    relation_service_mock.create_relation.return_value = relation_type_mock
    request_json = {}

    response = client.post(TYPE_LIST_ENDPOINT, json=request_json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_post__type_is_empty__return_422(client, relation_service_mock, relation_type_mock):
    relation_service_mock.create_relation.return_value = relation_type_mock
    request_json = {"type": ""}

    response = client.post(TYPE_LIST_ENDPOINT, json=request_json)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_put__return_200(client, relation_service_mock, relation_type_mock):
    relation_service_mock.update_relation_type.return_value = relation_type_mock["type"]

    response = client.put(DETAIL_ENDPOINT, json=relation_type_mock)

    assert response.status_code == HTTPStatus.OK


def test_put__incorrect_schema__return_422(client, relation_service_mock, relation_type_mock):
    relation_service_mock.update_relation_type.return_value = relation_type_mock["type"]

    relation_type_mock["type"] = ""
    response = client.put(DETAIL_ENDPOINT, json=relation_type_mock)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
