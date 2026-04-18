import random
from collections import namedtuple

import pytest
from faker import Faker

from deps_documents.domain.constants import AssignAction
from tests.factories import (
    DocumentListDataFactory,
    RelationEntityFactory,
    RelationListDataFactory,
)

RELATION_ENDPOINT = "/api/document/v1/relations"

relation_list_tuple = namedtuple("relation_list_tuple", ["endpoint", "url_values"])


@pytest.fixture
def relation_service_mock(mocker, domain_services):
    mock = mocker.Mock(domain_services.relation.cls)
    domain_services.relation.override(mock)

    return mock


def _relation_type():
    faker = Faker()
    return {"type": faker.word()}


@pytest.fixture
def relation_type_mock():
    yield _relation_type()


@pytest.fixture
def type_list_mock():
    relation_count = random.randint(0, 5)
    relation_types = [_relation_type()["type"] for _ in range(relation_count)]
    yield {
        "content": relation_types,
        "meta": {
            "total": random.randint(0, 5),
            "size": relation_count,
        },
    }


@pytest.fixture
def relation_post_body_mock():
    yield {
        "code": "Test unique key",
        "type": "Test relation type",
        "assignedDocuments": [1, 2],
    }


@pytest.fixture
def assign_post_body_mock():
    yield {
        "assignedDocuments": [1, 2],
    }


@pytest.fixture
def assign_patch_body_mock():
    yield assign_patch_generate_body()


def assign_patch_generate_body():
    return {"assignedDocuments": [1, 2], "action": random.choice(list(AssignAction)).value}


@pytest.fixture
def relation_put_body_mock():
    yield {
        "code": "Test unique key",
        "type": "Test relation type",
        "assignedDocuments": [1, 2],
        "parentCode": "Report",
        "parentType": "root",
    }


def assign_patch_generate_invalid_body_generator():
    body = assign_patch_generate_body()

    for key in body:
        invalid = assign_patch_generate_body()
        invalid.pop(key)
        yield invalid


@pytest.fixture
def relation_mock_list():
    return RelationListDataFactory()


@pytest.fixture
def relation_mock():
    return RelationEntityFactory()


@pytest.fixture
def document_mock_list(faker):
    patched_documents = DocumentListDataFactory()
    for doc in patched_documents.content:
        doc.pk = faker.random_int()
        doc.document_type = faker.word()
    yield patched_documents
