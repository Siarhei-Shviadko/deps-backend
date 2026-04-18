from http import HTTPStatus

import pytest

from deps_documents.domain.exceptions import (
    RelationChildrenNotFoundError,
    RelationNotFoundError,
)

from .test_list import DETAIL_ENDPOINT

CHILDREN_ENDPOINT = f"{DETAIL_ENDPOINT}/children"


def test_children_list__return_200(client, relation_service_mock, relation_mock_list):
    relation_service_mock.get_children_list.return_value = relation_mock_list

    response = client.get(CHILDREN_ENDPOINT)
    assert response.status_code == HTTPStatus.OK

    response_content = response.json()
    assert response_content["meta"]["total"] == relation_mock_list.meta.total
    assert response_content["meta"]["size"] == relation_mock_list.meta.size
    assert len(response_content["result"]) == len(relation_mock_list.content)


@pytest.mark.parametrize("exception", (RelationChildrenNotFoundError, RelationNotFoundError))
def test_get_children__raise_exception__return_404(client, relation_service_mock, exception, relation_mock):
    relation_service_mock.get_children_list.side_effect = exception(relation_mock)

    response = client.get(CHILDREN_ENDPOINT)

    assert response.status_code == HTTPStatus.NOT_FOUND
