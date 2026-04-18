import random

import pytest

from deps_documents.domain.exceptions import (
    AssignedDocumentDeletingError,
    DocumentAlreadyAssignedError,
    DocumentAssigningError,
    RelationNotFoundError,
)
from tests.factories import DocumentEntityFactory


def test_assigned_documents__assign_list__pass(relation_not_created_created_type_and_docs, relation_service):
    expected_relation = relation_not_created_created_type_and_docs
    actual_relation = relation_service.create_relation(relation=expected_relation)

    assert actual_relation == expected_relation


def test_assigned_documents__assign_empty_list__pass(relation_not_created_created_type_empty_docs, relation_service):
    expected_relation = relation_not_created_created_type_empty_docs
    actual_relation = relation_service.create_relation(relation=expected_relation)

    assert actual_relation == expected_relation


def test_assigned_documents__relation_not_exists__raise_error(
    relation_not_created_created_docs, relation_service, domain_services
):
    with pytest.raises(RelationNotFoundError):
        relation_service.assign_document(relation_not_created_created_docs)


def test_assigned_documents__docs_not_exists__raise_error(
    relation_created_docs_not_exists,
    relation_service,
):
    with pytest.raises(DocumentAssigningError):
        relation_service.assign_document(relation_created_docs_not_exists)


def test_assigned_documents__docs_already_assign__raise_error(
    relation_created_docs_exist_not_assigned,
    relation_service,
):
    relation = relation_created_docs_exist_not_assigned
    relation_service.assign_document(relation)
    with pytest.raises(DocumentAlreadyAssignedError):
        relation_service.assign_document(relation)


def test_delete_assigned_documents__relation_exists_docs_assigned_delete_all__pass(
    relation_service, relation_created_docs_exist_not_assigned
):
    relation = relation_created_docs_exist_not_assigned
    relation_service.assign_document(relation)
    relation_service.delete_assigned_documents(relation)


def test_delete_assigned_documents__relation_exists_docs_assigned_delete_few__pass(
    relation_service, relation_not_created_created_type, domain_services, uow
):
    relation = relation_not_created_created_type
    relation.assigned_documents = [
        int(domain_services.document().create(DocumentEntityFactory())) for _ in range(random.randint(3, 7))
    ]
    expected_docs = relation.assigned_documents[1::2]
    relation_service.create_relation(relation)
    relation.assigned_documents = relation.assigned_documents[::2]
    relation_service.delete_assigned_documents(relation)

    actual_docs = uow.relation.get_assigned_documents(relation)
    assert expected_docs == actual_docs


def test_delete_assigned_documents__relation_does_not_exist__raise_error(relation_service, relation_not_created_created_type):
    relation = relation_not_created_created_type
    with pytest.raises(RelationNotFoundError):
        relation_service.delete_assigned_documents(relation)


def test_delete_assigned_documents__documents_does_not_exist__raise_error(
    relation_service, relation_created_docs_exist_not_assigned
):
    relation = relation_created_docs_exist_not_assigned
    with pytest.raises(AssignedDocumentDeletingError):
        relation_service.delete_assigned_documents(relation)
