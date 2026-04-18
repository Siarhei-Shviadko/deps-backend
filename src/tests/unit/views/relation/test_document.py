from http import HTTPStatus

from deps_documents.domain.exceptions import RelationNotFoundError

from .test_list import DETAIL_ENDPOINT

DOCUMENT_ENDPOINT = f"{DETAIL_ENDPOINT}/documents"


def test_get_document__return_200(client, relation_service_mock, document_mock_list):
    relation_service_mock.get_document.return_value = document_mock_list

    response = client.get(DOCUMENT_ENDPOINT)

    assert response.status_code == HTTPStatus.OK
    result = response.json()
    assert result["meta"]["size"] == document_mock_list.meta.size
    assert result["meta"]["total"] == document_mock_list.meta.total
    assert len(result["result"]) == len(document_mock_list.content)


def test_get_document__relation_doesnt_exist__return_404(client, relation_service_mock, document_mock_list, relation_mock):
    relation_service_mock.get_document.side_effect = RelationNotFoundError(relation_mock)

    response = client.get(DOCUMENT_ENDPOINT)

    assert response.status_code == HTTPStatus.NOT_FOUND
