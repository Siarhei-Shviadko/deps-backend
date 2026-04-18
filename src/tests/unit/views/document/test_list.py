import json
from typing import Any, Dict
from uuid import uuid4

import pytest

from deps_documents.api.models.document.document import DocumentModel
from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.dtos import SortingFieldsEnum
from deps_documents.domain.entities import DocumentEntityPk
from deps_documents.domain.exceptions import DocumentAlreadyExistsError
from tests.factories import (
    DocumentEntityFactory,
    DocumentListDataFactory,
    GroupEntityFactory,
    ListResponseMetaDataFactory,
)
from tests.serializers import dump_document_for_request


class TestListView:
    def test_get__without_filters__return_200(self, client, document_service_mock):
        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get("/api/document/v1/documents")

        assert response.status_code == 200

    def test_get__without_filters__return_proper_fields(self, client, document_service_mock):
        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get("/api/document/v1/documents")
        response_json = response.json()

        assert "result" in response_json
        assert "meta" in response_json
        assert "total" in response_json["meta"]
        assert "size" in response_json["meta"]

    def test_get__without_filters__return_proper_fields_values(self, client, document_service_mock):
        group = GroupEntityFactory()

        documents = [
            DocumentEntityFactory(pk="1", group=group),
            DocumentEntityFactory(pk="2", group=group),
            DocumentEntityFactory(pk="a", group=group),
        ]
        meta_info = ListResponseMetaDataFactory(total=10, size=3)
        document_list = DocumentListDataFactory(meta=meta_info, content=documents)

        document_service_mock.get_document_list.return_value = document_list
        response = client.get("/api/document/v1/documents")
        response_json = response.json()

        assert len(response_json["result"]) == 3
        assert response_json["meta"]["total"] == 10
        assert response_json["meta"]["size"] == 3

        for document in response_json["result"]:
            parsed_document = DocumentModel(**document)
            assert parsed_document.group_id == group.id

    def test_get__with_valid_filters__return_200(self, client, document_service_mock):
        filters = self._build_filters()
        query = self._build_query(filters)
        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get(f"/api/document/v1/documents?{query}")

        assert response.status_code == 200

    @pytest.mark.parametrize("sort_field", [e.value for e in SortingFieldsEnum])
    def test_get__valid_sort_field__return_200(self, sort_field, client, document_service_mock):
        filters = self._build_filters(sort_field=sort_field)
        query = self._build_query(filters)
        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get(f"/api/document/v1/documents?{query}")

        assert response.status_code == 200

    @pytest.mark.parametrize("doc_state", [e.value for e in DocumentStateEnum])
    def test_get__valid_doc_state__return_200(self, doc_state, client, document_service_mock):
        filters = self._build_filters(doc_states=[doc_state])

        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        query = self._build_query(filters)

        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get(f"/api/document/v1/documents?{query}")

        assert response.status_code == 200

    def test_get__invalid_doc_state__return_400(self, client, document_service_mock):
        filters = self._build_filters()
        filters["states"] = ["labeling"]
        query = self._build_query(filters)
        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get(f"/api/document/v1/documents?{query}")

        assert response.status_code == 400

    def test_get__invalid_sort_field__return_422(self, client, document_service_mock):
        filters = self._build_filters()
        filters["sortField"] = "length"
        query = self._build_query(filters)
        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get(f"/api/document/v1/documents?{query}")

        assert response.status_code == 422

    def test_get__invalid_page__return_422(self, client, document_service_mock):
        filters = self._build_filters()
        filters["page"] = "one"
        query = self._build_query(filters)
        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get(f"/api/document/v1/documents?{query}")

        assert response.status_code == 422

    def test_get__invalid_per_page__return_422(self, client, document_service_mock):
        filters = self._build_filters()
        filters["perPage"] = "two"
        query = self._build_query(filters)

        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get(f"/api/document/v1/documents?{query}")

        assert response.status_code == 422

    def test_get__invalid_date_range__return_400(self, client, document_service_mock):
        filters = self._build_filters()
        filters["dateRange"] = "from 2 to 4"
        query = self._build_query(filters)

        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get(f"/api/document/v1/documents?{query}")

        assert response.status_code == 400

    def test_get__invalid_has_reviewer__return_422(self, client, document_service_mock):
        filters = self._build_filters()
        filters["hasReviewer"] = "has"
        query = self._build_query(filters)

        document_service_mock.get_document_list.return_value = DocumentListDataFactory()
        response = client.get(f"/api/document/v1/documents?{query}")

        assert response.status_code == 422

    def _build_filters(self, doc_states=None, sort_field=SortingFieldsEnum.pk.value) -> Dict[str, Any]:
        if doc_states is None:
            doc_states = [DocumentStateEnum.COMPLETED.value]
        filters = {
            "states": doc_states,
            "types": ["Some type"],
            "title": "Some title",
            "exceptTypes": [],
            "reviewer": "Some reviewer",
            "validation": [],
            "sources": [],
            "sortField": sort_field,
            "sortDirect": "decs",
            "page": 2,
            "perPage": 42,
            "labels": ["Some label"],
            "hasReviewer": True,
            "parentId": "Some parent_id",
        }

        return filters

    def test_post__valid_document__return_201_response(self, client, document_service_mock):
        document = DocumentEntityFactory()
        ser_document = dump_document_for_request(document)
        doc = {
            "document": {
                **ser_document,
            }
        }
        doc = json.dumps(doc)

        document_service_mock.create.return_value = "1"
        response = client.post("/api/document/v1/documents", data=doc)

        assert response.status_code == 201

    def test_post__valid_document__return_doc_id(self, client, document_service_mock):
        document = DocumentEntityFactory()
        ser_document = dump_document_for_request(document)
        doc = {
            "document": {
                **ser_document,
            }
        }
        doc = json.dumps(doc)

        document_service_mock.create.return_value = "1"
        response = client.post("/api/document/v1/documents", data=doc)
        response_json = response.json()

        assert "_id" in response_json

    def test_post__empty_body__return_422(self, client):
        doc = {"document": {}}
        doc = json.dumps(doc)
        response = client.post("/api/document/v1/documents", data=doc)

        assert response.status_code == 422

    def test_post__already_existing_document__return_409(self, client, document_service_mock):
        document = DocumentEntityFactory()
        ser_document = dump_document_for_request(document)
        doc = {
            "document": {
                **ser_document,
            }
        }
        doc = json.dumps(doc)

        document_service_mock.create.side_effect = DocumentAlreadyExistsError
        response = client.post("/api/document/v1/documents", data=doc)

        assert response.status_code == 409

    def test_put__valid_document__return_200_response(self, client, document_service_mock):
        document = DocumentEntityFactory()
        ser_document = dump_document_for_request(document)
        doc = {
            "document": {
                **ser_document,
            }
        }
        doc = json.dumps(doc)

        document_service_mock.update.return_value = "1"
        response = client.put("/api/document/v1/documents", data=doc)

        assert response.status_code == 200

    def test_put__valid_document__return_doc_id(self, client, document_service_mock):
        document = DocumentEntityFactory()
        ser_document = dump_document_for_request(document)
        doc = {
            "document": {
                **ser_document,
            }
        }
        doc = json.dumps(doc)

        document_service_mock.update.return_value = "1"
        response = client.put("/api/document/v1/documents", data=doc)
        response_json = response.json()

        assert "_id" in response_json

    def test_put__empty_body__return_422(self, client):
        doc = {"document": {}}
        doc = json.dumps(doc)
        response = client.put("/api/document/v1/documents", data=doc)

        assert response.status_code == 422

    def test_delete__valid_body__return_200(self, client, document_service_mock):
        document_service_mock.batch_delete.return_value = [DocumentEntityPk("1")]

        response = client.request("DELETE", "/api/document/v1/documents", json={"documentIds": ["1"]})

        assert response.status_code == 200

    def test_delete__valid_body__return_proper_fields(self, client, document_service_mock):
        document_service_mock.batch_delete.return_value = [DocumentEntityPk("1")]

        response = client.request("DELETE", "/api/document/v1/documents", json={"documentIds": ["1"]})
        response_json = response.json()

        assert "deletedDocumentKeys" in response_json

    def test_delete__valid_body__return_proper_fields_value(self, client, document_service_mock):
        expected_json = {
            "deletedDocumentKeys": [{"_id": "1"}],
        }
        document_service_mock.batch_delete.return_value = [DocumentEntityPk("1")]

        response = client.request("DELETE", "/api/document/v1/documents", json={"documentIds": ["1", "2"]})
        response_json = response.json()

        assert response_json == expected_json

    def test_delete__empty_document_id__return_422_response(self, client):
        response = client.request("DELETE", "/api/document/v1/documents", json={"documentIds": [""]})

        assert response.status_code == 422

    def _build_query(self, filters):
        query = "&".join(["{}={}".format(str(k), self._format_value_for_query(v)) for k, v in filters.items()])

        return query

    def _format_value_for_query(self, v, is_in=False):
        if isinstance(v, list):
            str_v = "[{}]".format(", ".join((self._format_value_for_query(sub_v, True) for sub_v in v)))
        elif isinstance(v, str):
            if is_in:
                str_v = '"{}"'.format(v)
            else:
                str_v = v
            str_v = str_v.replace(" ", "+")
        else:
            str_v = str(v)

        return str_v
