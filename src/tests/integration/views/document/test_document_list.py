import datetime
import json
from http import HTTPStatus
from itertools import product
from uuid import uuid4

import pytest

from deps_documents.domain.constants import DocumentStateEnum
from deps_documents.domain.dtos import SortingFieldsEnum
from tests.factories import DocumentEntityFactory, GroupEntityFactory, ReviewerFactory
from tests.serializers import dump_document_for_request
from tests.utils import ContainerDocumentCreatorMixin

from .utils import check_document_response_fields


class TestDocumentListEmptyDB:
    base_url = "/api/document/v1/documents"

    def test_get__without_filters__return_200_response(self, client):
        response = client.get(self.base_url)

        assert response.status_code == 200

    def test_get__without_filters__return_proper_response_fields(self, client):
        response = client.get(self.base_url)
        response_json = response.json()

        assert "result" in response_json
        assert "meta" in response_json
        assert "total" in response_json["meta"]
        assert "size" in response_json["meta"]

    def test_get__without_filters__return_proper_response_fields_values(self, client):
        response = client.get(self.base_url)
        response_json = response.json()

        assert len(response_json["result"]) == 0
        assert response_json["meta"]["total"] == 0
        assert response_json["meta"]["size"] == 0


class TestDocumentListFilledDB:
    base_url = "/api/document/v1/documents"

    @classmethod
    def setup_class(cls):
        cls.document_entity = DocumentEntityFactory()
        cls.total_entities = 20
        cls.document_entities = DocumentEntityFactory.create_batch(cls.total_entities)

    def test_get__without_filters__return_proper_response_fields(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]

        response = client.get(self.base_url)
        response_json = response.json()

        assert "result" in response_json

    def test_get__without_filters__return_result_fields(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]

        response = client.get(self.base_url)
        response_json = response.json()
        response_json = response_json["result"]

        assert response.status_code == 200 and len(response_json) > 0

    def test_get__without_filters__return_proper_document_fields(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]

        response = client.get(self.base_url)
        response_json = response.json()
        document_json = response_json["result"][0]

        check_document_response_fields(document_json)

    def test_post__valid_document__return_201_response(self, client):
        document = DocumentEntityFactory.create()
        ser_document = dump_document_for_request(document)
        doc = {
            "document": {
                **ser_document,
            }
        }

        doc = json.dumps(doc)

        response = client.post(self.base_url, data=doc)

        assert response.status_code == 201

    def test_post__valid_document__return_doc_id(self, client):
        document = DocumentEntityFactory.create()
        ser_document = dump_document_for_request(document)
        doc = {
            "document": {
                **ser_document,
            }
        }

        doc = json.dumps(doc)

        response = client.post(self.base_url, data=doc)
        response_json = response.json()

        assert "_id" in response_json

    def test_search_for_tesseract__return_only_tesseracted_docs(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]

        resp = client.get(self.base_url, params={"search": "tesseract"})

        assert resp.status_code == 200

        for doc in resp.json()["result"]:
            assert "tesseract" in doc["engine"].lower()

    def test_search_for_ready_docs__returns_only_completed_docs(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]

        resp = client.get(self.base_url, params={"search": "ready"})

        assert resp.status_code == 200

        for doc in resp.json()["result"]:
            assert "completed" == doc["state"].lower()

    def test_search_for_pattern_in_different_fields(self, client, uow):
        documents = [DocumentEntityFactory(title="postponed"), DocumentEntityFactory(state=DocumentStateEnum.FAILED)]
        [uow.document.add(document) for document in documents]

        resp = client.get(self.base_url, params={"search": "postponed"})

        assert resp.status_code == 200

        assert len(resp.json()["result"]) == 2
        assert resp.json()["result"][0]["state"] == "failed"
        assert resp.json()["result"][1]["title"] == "postponed"

    def test_search_for_upper_case(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]

        resp = client.get(self.base_url, params={"search": "EXTRACTION"})

        assert resp.status_code == 200

        for doc in resp.json()["result"]:
            assert "dataExtraction" == doc["state"]

    def test_search_part_of_text(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]

        resp = client.get(self.base_url, params={"search": "gcp"})

        assert resp.status_code == 200

        for doc in resp.json()["result"]:
            assert "GCP_VISION" == doc["engine"]

    def test_search_for_state(self, client, uow):
        [uow.document.add(document) for document in self.document_entities]

        resp = client.get(self.base_url, params={"search": "preprocessing"})

        assert resp.status_code == 200

        for doc in resp.json()["result"]:
            assert "preprocessing" == doc["state"]

    @pytest.mark.parametrize("char", ("%", "_"))
    def test_search__special_chars_as_input__correct_docs_returned(self, client, uow, char):
        [uow.document.add(document) for document in self.document_entities]

        doc = uow.document.add(DocumentEntityFactory(title=f"test{char}"))

        resp = client.get(self.base_url, params={"search": char})

        assert resp.status_code == 200
        assert resp.json()["result"][0]["title"] == doc.title


class TestDocumentListArguments(ContainerDocumentCreatorMixin):
    base_url = "/api/document/v1/documents"

    @pytest.mark.parametrize("test_state", [state.value for state in DocumentStateEnum])
    def test_get__valid_states_arg__return_200_response(self, client, test_state):
        response = client.get(self.base_url, params={"states": json.dumps([test_state])})

        assert response.status_code == 200

    def test_get__not_valid_states_enum_arg__return_400_response(self, client):
        response = client.get(self.base_url, params={"states": json.dumps(["qwerty"])})

        assert response.status_code == 400

    def test_get__not_valid_states_json_arg__return_400_response(self, client):
        response = client.get(self.base_url, params={"states": ""})

        assert response.status_code == 400

    def test_get__valid_document_type_arg__return_200_response(self, client):
        response = client.get(self.base_url, params={"types": json.dumps(["any"])})

        assert response.status_code == 200

    def test_get__valid_title_arg__return_200_response(self, client):
        response = client.get(self.base_url, params={"title": "any"})

        assert response.status_code == 200

    def test_get__valid_except_types_arg__return_200_response(self, client):
        response = client.get(self.base_url, params={"exceptTypes": json.dumps(["any"])})

        assert response.status_code == 200

    def test_get__valid_reviewer_arg__return_200_response(self, client):
        response = client.get(self.base_url, params={"reviewer": "any"})

        assert response.status_code == 200

    def test_get__valid_validation_arg__return_200_response(self, client):
        response = client.get(self.base_url, params={"validation": json.dumps(["Passed"])})

        assert response.status_code == 200

    def test_get__valid_source_arg__return_200_response(self, client):
        response = client.get(self.base_url, params={"sources": json.dumps(["any"])})

        assert response.status_code == 200

    @pytest.mark.parametrize("test_field", [field.value for field in SortingFieldsEnum])
    def test_get__valid_sort_field_arg__return_200_response(self, client, test_field):
        response = client.get(self.base_url, params={"sortField": test_field})

        assert response.status_code == 200

    def test_get__not_valid_sort_field_arg__return_422_response(self, client):
        response = client.get(self.base_url, params={"sortField": "qwerty"})

        assert response.status_code == 422

    def test_get__valid_sort_direct_arg__return_200_response(self, client):
        response = client.get(self.base_url, params={"sortDirect": "desc"})

        assert response.status_code == 200

    def test_get__valid_page_arg__return_200_response(self, client):
        response = client.get(self.base_url, params={"page": 1})

        assert response.status_code == 200

    def test_get__valid_per_page_arg__return_200_response(self, client):
        response = client.get(self.base_url, params={"perPage": 1})

        assert response.status_code == 200

    @pytest.mark.parametrize(
        "test_args,expected_code",
        [(args, 200) for args in product([None, datetime.datetime.now(datetime.timezone.utc)], repeat=2)],
    )
    def test_get__date_range(self, client, mocker, test_args, expected_code):
        test_args = [arg.isoformat() if arg else arg for arg in test_args]
        response = client.get(self.base_url, params={"dateRange": json.dumps(test_args)})

        assert response.status_code == expected_code

    def test_delete__valid_data__response_200(self, client, uow):
        document = uow.document.add(DocumentEntityFactory(pk=1))
        response = client.request("DELETE", self.base_url, json={"documentIds": [str(document.pk)]})
        expected_json = {
            "deletedDocumentKeys": [{"_id": str(document.pk)}],
        }

        assert response.status_code == 200
        assert response.json() == expected_json

    @pytest.mark.parametrize("document_id", [0, -1, "someNotExistingDocumentId"])
    def test_delete__valid_data__invalid_params(self, client, document_id):
        response = client.request("DELETE", self.base_url, json={"documentIds": [str(document_id)]})
        assert response.status_code == 422

    @pytest.mark.parametrize("document_id", [999999999])
    def test_delete__valid_data__no_document__no_error(self, client, document_id):
        response = client.request("DELETE", self.base_url, json={"documentIds": [str(document_id)]})
        assert response.status_code == 404

    def test_get__valid_has_reviewer_arg__return_200_response(self, client, uow):
        uow.document.add(DocumentEntityFactory(reviewer=None))
        reviewer = uow.document._save_reviewer(ReviewerFactory())
        document_has_reviewer = uow.document.add(DocumentEntityFactory(reviewer=reviewer))

        response = client.get(self.base_url, params={"hasReviewer": True})
        assert response.status_code == 200
        response_json = response.json()["result"]
        assert len(response_json) == 1
        assert document_has_reviewer.pk == response_json[0]["_id"]

    def test_get__valid_has_no_reviewer_arg__return_200_response(self, client, uow):
        document_has_no_reviewer = uow.document.add(DocumentEntityFactory(reviewer=None))
        reviewer = uow.document._save_reviewer(ReviewerFactory())
        uow.document.add(DocumentEntityFactory(reviewer=reviewer))

        response = client.get(self.base_url, params={"hasReviewer": False})
        assert response.status_code == 200
        response_json = response.json()["result"]
        assert len(response_json) == 1
        assert document_has_no_reviewer.pk == response_json[0]["_id"]

    def test_get__valid_has_no_reviewer_and_state_completed__return_200_response(self, client, uow):
        document_has_no_reviewer = uow.document.add(DocumentEntityFactory(reviewer=None, state=DocumentStateEnum.COMPLETED))
        reviewer = uow.document._save_reviewer(ReviewerFactory())
        uow.document.add(DocumentEntityFactory(reviewer=reviewer, state=DocumentStateEnum.COMPLETED))
        response = client.get(
            self.base_url, params={"hasReviewer": False, "states": json.dumps([DocumentStateEnum.COMPLETED.value])}
        )
        assert response.status_code == 200
        response_json = response.json()["result"]
        assert len(response_json) == 1
        assert document_has_no_reviewer.pk == response_json[0]["_id"]

    def test_get__parents_argument_true__return_200_response(self, client, uow):
        self._create_email_container_doc(uow)

        response = client.get(self.base_url, params={"parentId": "null"})

        assert response.status_code == HTTPStatus.OK

    def test_get__parents_argument_true__return_only_top_level_parents_doc(self, client, uow):
        parent_doc, _ = self._create_email_container_doc(uow)

        response = client.get(self.base_url, params={"parentId": "null"})

        response_json = response.json()["result"]
        assert len(response_json) == 1
        assert response_json[0]["_id"] == parent_doc.pk

    def test_get__parent_id_argument_provided__return_200_response(self, client, uow):
        parent_doc, _ = self._create_email_container_doc(uow)

        response = client.get(self.base_url, params={"parentId": parent_doc.pk})

        assert response.status_code == HTTPStatus.OK

    def test_get__parent_id_argument_provided__return_only_child_documents(self, client, uow):
        number_of_childs = 10
        parent_doc, _ = self._create_email_container_doc(uow, child_docs_number=number_of_childs)

        response = client.get(self.base_url, params={"parentId": parent_doc.pk})

        response_json = response.json()["result"]
        assert len(response_json) == number_of_childs

    @pytest.mark.parametrize("char", ("%", "_"))
    def test_get__special_characters_in_title__correct_docs_returned(self, client, uow, char):
        doc = uow.document.add(DocumentEntityFactory(title=f"test{char}"))

        response = client.get(self.base_url, params={"title": char})

        response_json = response.json()["result"][0]
        assert response_json["title"] == doc.title

    def test_get__ids__correct_docs_returned(self, client, uow):
        document = uow.document.add(DocumentEntityFactory(pk=2))
        ids = json.dumps([document.pk])

        response = client.get(self.base_url, params={"ids": ids})

        response_json = response.json()["result"][0]
        assert response_json["_id"] == document.pk
        assert len(response.json()["result"]) == 1

    def test_get__ids__correct_no_result(self, client, uow):
        ids = json.dumps([2])
        response = client.get(self.base_url, params={"ids": ids})

        response_meta = response.json()["meta"]
        assert response_meta["total"] == 0
        assert response_meta["size"] == 0
        assert len(response.json()["result"]) == 0

    def test_get__group_filter(self, client, uow, tenant_id: str):
        groups = GroupEntityFactory.create_batch(2)

        for group in groups:
            uow.group.save(group_id=group.id, tenant_id=tenant_id, name=group.name)

        documents = [
            DocumentEntityFactory(pk="1", group=groups[0]),
            DocumentEntityFactory(pk="2", group=groups[1]),
        ]
        for document in documents:
            uow.document.add(document)

        response = client.get(self.base_url, params={"groups": json.dumps([groups[0].id])})

        response_meta = response.json()["meta"]
        assert response_meta["total"] == 1
        assert response_meta["size"] == 1
        assert len(response.json()["result"]) == 1
