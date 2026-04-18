import random

import pytest

from deps_documents.domain.dtos import (
    RelationDataObject,
    RelationFilterObject,
    UpdateRelationEntity,
)
from deps_documents.domain.entities import RelationEntity
from deps_documents.domain.exceptions import (
    DocumentAlreadyAssignedError,
    RelationAlreadyExistsError,
    RelationChildrenNotFoundError,
    RelationNotFoundError,
    RelationParentNotFoundError,
    RelationTypeNotFoundError,
    RelationUpdatingError,
)
from tests.factories import RelationEntityFactory

from .conftest import generate_child_relation


def test_create_relation__without_docs__equal(relation_not_created_empty_docs, relation_service):
    expected = relation_not_created_empty_docs
    relation_service.create_relation_type(expected.type)
    actual_relation = relation_service.create_relation(expected)

    assert actual_relation == expected


def test_create_relation__without_docs__in_get_list(relation_not_created_created_type_empty_docs, relation_service, uow):
    expected = relation_not_created_created_type_empty_docs
    relation_service.create_relation(expected)

    relation_filter = RelationFilterObject(
        code=expected.code,
        type=expected.type,
    )
    actual_relation_list = uow.relation.get_relation_list(relation_filter)

    assert expected in actual_relation_list


def test_create_relation__without_type__raise_error(relation_not_created, relation_service):
    with pytest.raises(RelationTypeNotFoundError):
        relation_service.create_relation(relation_not_created)


def test_create_relation__with_docs__in_relation_list(
    relation_not_created_created_type_and_docs,
    relation_service,
):
    expected = relation_not_created_created_type_and_docs
    actual_relation = relation_service.create_relation(expected)

    assert actual_relation == expected


def test_create_relation__create_the_same__exist_error(relation_not_created_created_type_empty_docs, relation_service):
    relation = relation_not_created_created_type_empty_docs
    relation_service.create_relation(relation)

    with pytest.raises(RelationAlreadyExistsError):
        relation_service.create_relation(relation)


def test_get_relation_list__last_created_in_list_the_same_type__pass(relation_service, relation_list_with_created_type):
    relation_type = relation_list_with_created_type[0].type
    for relation in relation_list_with_created_type:
        relation.type = relation_type
        relation.assigned_documents = []

    expected_list = [relation_service.create_relation(expected_relation) for expected_relation in relation_list_with_created_type]

    relation_filter = RelationFilterObject(type=relation_type)
    actual_list = relation_service.get_relation_list(relation_filter).content

    assert expected_list == actual_list


def test_get_relation_list__last_created_in_list__pass(relation_service, relation_list_with_created_type):
    relation_list = relation_list_with_created_type
    for relation in relation_list:
        relation.assigned_documents = []

    expected_list = [relation_service.create_relation(expected_relation) for expected_relation in relation_list]

    actual_list = relation_service.get_relation_list().content

    assert expected_list == actual_list


def test_get_relation_list__find_one_value__pass(relation_service, relation_created_empty_docs):
    expected_relation = relation_created_empty_docs
    expected_list = [expected_relation]
    actual_list = relation_service.get_relation_list(
        RelationFilterObject(code=expected_relation.code, type=expected_relation.type)
    )

    assert len(expected_list) == actual_list.meta.size
    assert len(expected_list) == actual_list.meta.total
    assert expected_list == actual_list.content
    assert isinstance(actual_list, RelationDataObject)


def test_get_relation_list_filter__does_not_exists__raise_error(
    relation_service,
    relation_not_created,
):
    with pytest.raises(RelationNotFoundError):
        relation_service.get_relation_list(relation_not_created)


def test_update_relation__rename_relation__pass(
    relation_service, relation_created_empty_docs, relation_not_created_created_type_and_docs
):
    old_relation = relation_created_empty_docs
    expected_relation = RelationEntityFactory(type=old_relation.type, assigned_documents=[])
    actual_relation = relation_service.update(relation=old_relation, relation_update_info=expected_relation)
    assert expected_relation == actual_relation


def test_update_relation__update_meta_field__pass(relation_service, relation_created_empty_docs, relation_not_created, faker):
    expected_relation = relation_created_empty_docs
    update_info = UpdateRelationEntity(metadata=faker.pydict(nb_elements=random.randint(3, 5), value_types=("str", "int")))
    expected_relation.metadata = update_info.metadata
    actual_relation = relation_service.update(relation=expected_relation, relation_update_info=expected_relation)

    assert expected_relation == actual_relation


def test_update_relation__relation_does_not_exist(relation_service, relation_not_created_created_type_and_docs):
    old_relation = RelationEntityFactory()
    expected_relation = relation_not_created_created_type_and_docs
    with pytest.raises(RelationNotFoundError):
        relation_service.update(relation=old_relation, relation_update_info=expected_relation)


def test_update_relation__rename_to_exists_relation__raise_error(
    relation_service,
    relation_created_empty_docs,
):
    exist_relation = relation_created_empty_docs
    new_created_relation = RelationEntityFactory(type=exist_relation.type, assigned_documents=[])
    relation_service.create_relation(relation=new_created_relation)
    with pytest.raises(RelationUpdatingError):
        relation_service.update(
            relation=exist_relation, relation_update_info=UpdateRelationEntity(code=new_created_relation.code)
        )


def test_update__rename_relation__assigned_docs_the_same(relation_service, relation_created_docs_assigned):
    old_relation = relation_created_docs_assigned
    new_relation = RelationEntityFactory()
    expected_relation = relation_service.update(
        relation=old_relation, relation_update_info=UpdateRelationEntity(code=new_relation.code)
    )
    actual_relation = relation_service.get_relation(RelationEntity(code=new_relation.code, type=old_relation.type))
    assert actual_relation == expected_relation
    assert actual_relation.code != old_relation.code


def test_update__rename_relation_and_docs_long_list(
    relation_service,
    relation_created_docs_exist_not_assigned,
):
    old_relation = relation_created_docs_exist_not_assigned
    docs_replace = old_relation.assigned_documents
    old_relation.assigned_documents = old_relation.assigned_documents[:-1]
    relation_service.assign_document(old_relation)

    new_relation = RelationEntityFactory()

    with pytest.raises(DocumentAlreadyAssignedError):
        relation_service.update(
            relation=old_relation,
            relation_update_info=UpdateRelationEntity(code=new_relation.code, assigned_documents=docs_replace),
        )


def test_update__rename_relation_and_docs_short_list(
    relation_service,
    relation_created_docs_exist_not_assigned,
):
    old_relation = relation_created_docs_exist_not_assigned
    docs_part = old_relation.assigned_documents[-1:]
    old_relation.assigned_documents = old_relation.assigned_documents[:-1]
    relation_service.assign_document(old_relation)

    new_relation = RelationEntityFactory()

    expected_relation = relation_service.update(
        relation=old_relation, relation_update_info=UpdateRelationEntity(code=new_relation.code, assigned_documents=docs_part)
    )
    actual_relation = relation_service.get_relation(RelationEntity(code=new_relation.code, type=old_relation.type))
    assert actual_relation == expected_relation
    assert actual_relation.assigned_documents == old_relation.assigned_documents + docs_part


def test_delete_relation__relation_exist__pass(relation_service, relation_created_docs_not_exists):
    relation_service.delete_relation(relation_created_docs_not_exists)


def test_delete_relation__relation_exist_docs_assigned__pass(relation_service, relation_created_docs_exist_not_assigned):
    relation = relation_created_docs_exist_not_assigned

    relation_service.assign_document(
        relation=relation,
    )

    relation_service.delete_relation(relation=relation)


def test_delete_relation__relation_does_not_exists__raise_error(relation_service, relation_not_created):
    with pytest.raises(RelationNotFoundError):
        relation_service.delete_relation(relation=relation_not_created)


def test_get_relation_list__created_child_in_list__pass(relation_service, relation_created_empty_docs):
    root_relation = relation_created_empty_docs
    expected_children = []
    for relation in generate_child_relation(root_relation.type, root_relation.code):
        relation_service.create_relation_type(relation.type)
        relation.assigned_documents = []
        expected_children.append(relation_service.create_relation(relation=relation))

    actual_children = relation_service.get_children_list(relation=root_relation)
    assert len(expected_children) == actual_children.meta.size
    assert len(expected_children) == actual_children.meta.total
    assert expected_children == actual_children.content


def test_get_relation_list__no_children__raise_error(relation_service, relation_created_empty_docs):
    root_relation = relation_created_empty_docs
    with pytest.raises(RelationChildrenNotFoundError):
        relation_service.get_children_list(relation=root_relation)


def test_get_relation_list__relation_does_not_exist__raise_error(relation_service, relation_not_created):
    root_relation = relation_not_created
    with pytest.raises(RelationNotFoundError):
        relation_service.get_children_list(relation=root_relation)


def test_create_relation__parent_does_not_exists__raise_error(relation_service, relation_not_created_created_type):
    relation = relation_not_created_created_type
    parent_relation = RelationEntityFactory(assigned_documents=[])
    relation.parent_code, relation.parent_type = parent_relation.code, parent_relation.type
    with pytest.raises(RelationParentNotFoundError):
        relation_service.create_relation(relation=relation)
