import random

import pytest

from deps_documents.domain.entities import parsing_feature
from deps_documents.domain.exceptions import (
    DocumentAlreadyExistsError,
    DocumentNotFoundError,
)
from tests.factories import (
    CommunicationEntityFactory,
    DocumentEntityFactory,
    ReviewerFactory,
)


@pytest.fixture
def document_entity():
    yield DocumentEntityFactory(communication=CommunicationEntityFactory(comments=[]))


def test_create__new_document__return_document(uow, document_entity):
    result = uow.document.add(document_entity)

    assert result.pk is not None


def test_create__document_already_exists__raises_error(uow, document_entity):
    result = uow.document.add(document_entity)

    with pytest.raises(DocumentAlreadyExistsError):
        uow.document.add(result)


def test_create__new_document_with_parent__return_document(uow):
    parent = uow.document.add(DocumentEntityFactory())
    child = DocumentEntityFactory(parent_id=parent.pk)

    result = uow.document.add(child)

    assert result.pk is not None


def test_create__new_document_with_parent__return_document_with_parent_id(uow):
    parent = uow.document.add(DocumentEntityFactory())
    child = DocumentEntityFactory(parent_id=parent.pk)

    result = uow.document.add(child)

    assert result.parent_id == parent.pk


def test_create__processing_params_saving(uow):
    document = DocumentEntityFactory(
        needs_parsing=False,
        parsing_features={},
        needs_unification=False,
        needs_extraction=False,
    )

    result = uow.document.add(document)

    assert not any([result.needs_parsing, result.needs_unification, result.needs_extraction, result.parsing_features])


def test_list__documents_exist__return_documents(uow, document_entity):
    uow.document.add(document_entity)
    document1 = uow.document.add(document_entity)
    document2 = uow.document.add(document_entity)

    result = uow.document.find_by_pks(document_pks=[document1.pk, document2.pk])
    assert sorted([r.pk for r in result]) == sorted([document1.pk, document2.pk])


def test_list__documents_not_exist__raise_document_not_found(uow):
    with pytest.raises(DocumentNotFoundError):
        uow.document.find_by_pks(document_pks=["12", "67", "42"])


@pytest.mark.parametrize("parsing_features", [{}, {parsing_feature.ParsingFeature.TEXT}])
def test_create__processing_params_with_workflow_params__saved(parsing_features, uow):
    needs_review = random.choice(["always_review", "never_review", "review_if_validation_failed"])
    needs_validation = random.choice([True, False])
    needs_output_exporting = random.choice([True, False])

    document = DocumentEntityFactory(
        needs_parsing=None,
        parsing_features=parsing_features,
        needs_unification=False,
        needs_extraction=False,
        needs_review=needs_review,
        needs_validation=needs_validation,
        needs_output_exporting=needs_output_exporting,
    )

    result = uow.document.add(document)

    assert result.needs_review == needs_review
    assert result.needs_validation == needs_validation
    assert result.needs_output_exporting == needs_output_exporting
    assert result.needs_parsing == bool(parsing_features)


def test_get__document_exist__return_document(uow, document_entity):
    document = uow.document.add(document_entity)

    result = uow.document.get(pk=document.pk)

    assert result.pk == document.pk


def test_get__document_not_exist__raise_document_not_found(uow):
    with pytest.raises(DocumentNotFoundError):
        uow.document.get(pk="1839")


def test_update__document_exists_update_document(uow, document_entity):
    document = uow.document.add(document_entity)
    updated_document = DocumentEntityFactory(pk=document.pk, communication=CommunicationEntityFactory(comments=[]))
    uow.document.update(updated_document)
    result = uow.document.get(document.pk)

    assert result == updated_document


def test_update__document_not_exists_raise_document_not_found(uow, document_entity):
    uow.document.add(document_entity)
    updated_document = DocumentEntityFactory(pk="999")

    with pytest.raises(DocumentNotFoundError):
        uow.document.update(updated_document)


def test_delete__document_exist__return_true(uow, document_entity):
    document = uow.document.add(document_entity)

    result = uow.document.delete(entity=document)

    assert result


def test_delete__document_not_exist__return_false(uow):
    document_entity = DocumentEntityFactory(pk="1712")

    result = uow.document.delete(document_entity)

    assert not result


def test_delete__child_document__return_true(uow):
    parent = uow.document.add(DocumentEntityFactory())
    child = DocumentEntityFactory(parent_id=parent.pk)
    child = uow.document.add(child)

    result = uow.document.delete(child)

    assert result


def test_delete__parent_document__return_true(uow):
    parent = uow.document.add(DocumentEntityFactory())
    child = DocumentEntityFactory(parent_id=parent.pk)
    uow.document.add(child)

    result = uow.document.delete(parent)

    assert result


def test_delete__parent_document__child_also_deleted(uow):
    parent = uow.document.add(DocumentEntityFactory())
    child = DocumentEntityFactory(parent_id=parent.pk)
    child = uow.document.add(child)
    child2 = DocumentEntityFactory(parent_id=child.pk)
    child2 = uow.document.add(child2)

    uow.document.delete(parent)

    with pytest.raises(DocumentNotFoundError):
        uow.document.get(child2.pk)


def test_batch_update__two_document__documents_updated(uow):
    doc1 = uow.document.add(DocumentEntityFactory())
    doc2 = uow.document.add(DocumentEntityFactory())

    new_reviewer = uow.document._save_reviewer(ReviewerFactory())
    doc1.reviewer = new_reviewer
    doc2.title = "Some new title"

    docs = uow.document.batch_update([doc1, doc2])

    assert docs == [doc1, doc2]


def test_batch_update__reviewer_saved_with_document(uow):
    reviewer = ReviewerFactory()
    doc1 = uow.document.add(DocumentEntityFactory(reviewer=reviewer))

    docs = uow.document.batch_update([doc1])

    assert docs[0].reviewer == reviewer
