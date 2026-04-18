import random

import pytest

from tests.factories import DocumentEntityFactory, RelationEntityFactory

RELATION_ENDPOINT = "/api/document/v1/relations"
DETAIL_ENDPOINT_FORMAT = f"{RELATION_ENDPOINT}/" + "{type}/{code}"


@pytest.fixture(scope="function")
def relation_not_created():
    yield RelationEntityFactory()


@pytest.fixture(scope="function")
def document_service(domain_services):
    yield domain_services.document()


@pytest.fixture(scope="function")
def relation_service(domain_services):
    yield domain_services.relation()


@pytest.fixture
def relation_not_created_docs_exists(relation_not_created, document_service):
    docs = [int(document_service.create(DocumentEntityFactory())) for _ in range(len(relation_not_created.assigned_documents))]
    relation_not_created.assigned_documents = docs
    return relation_not_created


@pytest.fixture
def created_relation_with_created_docs_not_assigned(document_service, relation_service, relation_not_created):
    docs = [int(document_service.create(DocumentEntityFactory())) for _ in range(len(relation_not_created.assigned_documents))]
    relation_not_created.assigned_documents = []

    relation_service.create_relation_type(relation_not_created.type)
    relation = relation_service.create_relation(relation_not_created)
    relation.assigned_documents = docs
    return relation


@pytest.fixture
def created_relation_with_assigned_docs(relation_service, created_relation_with_created_docs_not_assigned):
    relation = created_relation_with_created_docs_not_assigned

    relation_service.assign_document(relation)
    return relation
