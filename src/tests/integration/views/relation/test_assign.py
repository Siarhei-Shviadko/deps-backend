from http import HTTPStatus

from deps_documents.domain.constants import AssignAction
from deps_documents.domain.entities import RelationEntity

from .conftest import DETAIL_ENDPOINT_FORMAT

ASSIGN_ENDPOINT_FORMAT = f"{DETAIL_ENDPOINT_FORMAT}/assign"


def get_assign_endpoint(relation: RelationEntity):
    return ASSIGN_ENDPOINT_FORMAT.format(
        type=relation.type,
        code=relation.code,
    )


def test_assign_post__valid_data__return_201(client, created_relation_with_created_docs_not_assigned, relation_service):
    relation = created_relation_with_created_docs_not_assigned

    relation_before = relation_service.get_relation(relation)
    json_body = {"assignedDocuments": relation.assigned_documents}

    response = client.post(get_assign_endpoint(relation), json=json_body)

    relation_after = relation_service.get_relation(relation)

    assert response.status_code == HTTPStatus.CREATED
    assert relation_before.assigned_documents == []
    assert relation_after.assigned_documents == relation.assigned_documents


def test_assign_post__already_assigned__return_422(client, created_relation_with_created_docs_not_assigned, relation_service):
    relation = created_relation_with_created_docs_not_assigned

    relation.assigned_documents, additional_doc = relation.assigned_documents[:-1], relation.assigned_documents
    relation_service.assign_document(relation)

    json_body = {"assignedDocuments": additional_doc}

    response = client.post(get_assign_endpoint(relation), json=json_body)

    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_assign_post__relation_does_not_exist__return_404(client, relation_not_created_docs_exists):
    relation = relation_not_created_docs_exists
    json_body = {"assignedDocuments": relation.assigned_documents}

    response = client.post(get_assign_endpoint(relation), json=json_body)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_assign_delete__return_200(client, created_relation_with_assigned_docs, relation_service):
    relation = created_relation_with_assigned_docs

    relation_before = relation_service.get_relation(relation)

    response = client.delete(get_assign_endpoint(relation))

    relation_after = relation_service.get_relation(relation)

    assert response.status_code == HTTPStatus.OK
    assert relation_before.assigned_documents == relation.assigned_documents
    assert relation_after.assigned_documents == []


def test_assign_delete__relation_does_not_exist__return_404(client, relation_not_created_docs_exists):
    relation = relation_not_created_docs_exists

    response = client.delete(get_assign_endpoint(relation))

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_assign_patch__add__return_200(client, created_relation_with_created_docs_not_assigned, relation_service):
    relation = created_relation_with_created_docs_not_assigned
    relation.assigned_documents, additional_doc = relation.assigned_documents[:-1], relation.assigned_documents[-1:]
    relation_service.assign_document(relation)
    assign_patch_body = {"action": AssignAction.ADD.value, "assignedDocuments": additional_doc}
    response = client.patch(get_assign_endpoint(relation), json=assign_patch_body)

    assert response.status_code == HTTPStatus.CREATED


def test_assign_patch__add__return_404(client, relation_not_created_docs_exists, relation_service):
    relation = relation_not_created_docs_exists
    assign_patch_body = {"action": AssignAction.ADD.value, "assignedDocuments": relation.assigned_documents}
    response = client.patch(get_assign_endpoint(relation), json=assign_patch_body)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_assign_patch__delete__return_200(client, created_relation_with_created_docs_not_assigned, relation_service):
    relation = created_relation_with_created_docs_not_assigned
    doc_for_delete = relation.assigned_documents[-1:]
    relation_service.assign_document(relation)
    assign_patch_body = {"action": AssignAction.DELETE.value, "assignedDocuments": doc_for_delete}
    response = client.patch(get_assign_endpoint(relation), json=assign_patch_body)

    assert response.status_code == HTTPStatus.CREATED


def test_assign_patch__delete__return_422(client, created_relation_with_created_docs_not_assigned, relation_service, faker):
    relation = created_relation_with_created_docs_not_assigned

    doc_for_delete = max(relation.assigned_documents) + faker.pyint()

    relation_service.assign_document(relation)
    assign_patch_body = {"action": AssignAction.DELETE.value, "assignedDocuments": doc_for_delete}
    response = client.patch(get_assign_endpoint(relation), json=assign_patch_body)

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
