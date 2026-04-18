import pytest

from deps_documents.domain.dtos import UpdateRelationEntity
from deps_documents.domain.exceptions import (
    RelationTypeAlreadyExistsError,
    RelationTypeNotFoundError,
    RelationTypeUpdatingError,
)


def test_get_relation_type_list__create_relation_type__in_type_list(relation_not_created, relation_service):
    relation_service.create_relation_type(relation_type=relation_not_created.type)
    actual_relation_type_list = relation_service.get_relation_type_list().content

    assert relation_not_created.type in actual_relation_type_list


def test_create_relation_type__create_the_same__exist_error(relation_not_created, relation_service):
    relation_service.create_relation_type(relation_type=relation_not_created.type)
    with pytest.raises(RelationTypeAlreadyExistsError):
        relation_service.create_relation_type(relation_type=relation_not_created.type)


def test_update_relation_type__rename_one_type__pass(relation_service, relation_not_created_created_type, faker):
    old_relation_type = relation_not_created_created_type.type
    expected_relation_type = faker.word()
    actual_relation_type = relation_service.update_relation_type(
        relation_type=old_relation_type, type_update_info=expected_relation_type
    )
    assert expected_relation_type == actual_relation_type


def test_update_relation_type__rename_one_type__in_type_list(relation_service, relation_not_created_created_type, faker):
    old_relation_type = relation_not_created_created_type.type
    expected_relation_type = faker.word()
    relation_service.update_relation_type(relation_type=old_relation_type, type_update_info=expected_relation_type)
    actual_type_list = relation_service.get_relation_type_list().content
    assert expected_relation_type in actual_type_list


def test_update_relation_type__rename_to_exists_type__raise_error(relation_service, relation_not_created_created_type, faker):
    old_relation_type = relation_not_created_created_type.type
    existed_type = faker.word()
    relation_service.create_relation_type(relation_type=existed_type)

    with pytest.raises(RelationTypeUpdatingError):
        relation_service.update_relation_type(relation_type=old_relation_type, type_update_info=existed_type)


def test_update_relation_type__rename_does_not_exist_type__raise_error(relation_service, faker):
    old_relation_type = faker.word()
    existed_type = faker.word()
    with pytest.raises(RelationTypeNotFoundError):
        relation_service.update_relation_type(relation_type=old_relation_type, type_update_info=existed_type)


def test_update_relation_type__assigned_few_relation__pass(
    relation_service,
    created_relation_list_same_type,
    faker,
):
    old_relation_type = created_relation_list_same_type[0].type
    expected_relation_type = faker.word()

    expected_relation_list = created_relation_list_same_type
    for relation in expected_relation_list:
        relation.type = expected_relation_type

    relation_service.update_relation_type(relation_type=old_relation_type, type_update_info=expected_relation_type)

    actual_relation_list = relation_service.get_relation_list(UpdateRelationEntity(type=expected_relation_type)).content
    assert expected_relation_list == actual_relation_list
