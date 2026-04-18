import pytest

from tests.factories import DocumentEntityFactory, RelationEntityFactory


@pytest.fixture
def relation_not_created():
    yield RelationEntityFactory()


@pytest.fixture
def relation_service(domain_services):
    yield domain_services.relation()


@pytest.fixture(scope="function")
def document_service(domain_services):
    yield domain_services.document()


@pytest.fixture
def relation_with_docs(relation_service, relation_not_created, document_service):
    relation_service.create_relation_type(relation_not_created.type)
    docs = [int(document_service.create(DocumentEntityFactory())) for _ in range(len(relation_not_created.assigned_documents))]
    relation_not_created.assigned_documents = docs
    return relation_service.create_relation(relation_not_created)
