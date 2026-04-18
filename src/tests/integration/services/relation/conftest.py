import random

import pytest

from tests.factories import DocumentEntityFactory, RelationEntityFactory


@pytest.fixture(scope="function")
def relation_service(domain_services):
    yield domain_services.relation()


@pytest.fixture(scope="function")
def relation_not_created():
    yield RelationEntityFactory()


@pytest.fixture(scope="function")
def relation_not_created_created_type(uow, relation_not_created):
    uow.relation.create_relation_type(relation_type=relation_not_created.type)
    yield relation_not_created


@pytest.fixture(scope="function")
def relation_not_created_empty_docs(relation_not_created):
    relation_not_created.assigned_documents = []
    yield relation_not_created


@pytest.fixture(scope="function")
def relation_not_created_created_type_empty_docs(relation_not_created_created_type):
    relation_not_created_created_type.assigned_documents = []
    yield relation_not_created_created_type


def create_docs_for_relation(relation, doc_service):
    return [int(doc_service.create(DocumentEntityFactory())) for _ in range(len(relation.assigned_documents))]


@pytest.fixture(scope="function")
def relation_not_created_created_docs(relation_not_created, domain_services):
    relation_not_created.assigned_documents = create_docs_for_relation(relation_not_created, domain_services.document())
    yield relation_not_created


@pytest.fixture(scope="function")
def relation_not_created_created_type_and_docs(relation_not_created_created_type, domain_services):
    relation_not_created_created_type.assigned_documents = create_docs_for_relation(
        relation_not_created_created_type, domain_services.document()
    )
    yield relation_not_created_created_type


@pytest.fixture(scope="function")
def relation_created_docs_not_exists(relation_not_created_created_type, uow):
    relation = relation_not_created_created_type
    uow.relation.create_relation(relation)
    yield relation


@pytest.fixture(scope="function")
def relation_created_empty_docs(relation_created_docs_not_exists):
    relation_created_docs_not_exists.assigned_documents = []
    yield relation_created_docs_not_exists


@pytest.fixture(scope="function")
def relation_created_docs_exist_not_assigned(relation_not_created_created_type, uow, domain_services):
    relation = uow.relation.create_relation(relation_not_created_created_type)
    relation.assigned_documents = create_docs_for_relation(relation_not_created_created_type, domain_services.document())
    relation.assigned_documents = create_docs_for_relation(relation_not_created_created_type, domain_services.document())
    yield relation


@pytest.fixture(scope="function")
def relation_created_docs_assigned(uow, relation_created_docs_exist_not_assigned):
    relation = relation_created_docs_exist_not_assigned
    uow.relation.assign_document(relation)
    yield relation


@pytest.fixture(scope="function")
def relation_list_with_created_type(uow):
    relation_list = []
    for _ in range(random.randint(1, 5)):
        relation = RelationEntityFactory()
        uow.relation.create_relation_type(relation.type)
        relation_list.append(relation)
    yield relation_list


@pytest.fixture(scope="function")
def created_relation_list(uow, relation_list_with_created_type):
    for relation in relation_list_with_created_type:
        uow.relation.create_relation(relation)
    yield relation_list_with_created_type


@pytest.fixture(scope="function")
def created_relation_list_same_type(uow, relation_list_with_created_type):
    relation_list = []
    relation_type = relation_list_with_created_type[0].type
    for relation in relation_list_with_created_type:
        relation.type = relation_type
        relation_list.append(uow.relation.create_relation(relation))
    yield relation_list


def generate_child_relation(parent_type, parent_code, count=3):
    return [RelationEntityFactory(parent_type=parent_type, parent_code=parent_code) for _ in range(count)]
