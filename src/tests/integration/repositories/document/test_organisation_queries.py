import pytest

from tests.factories import CommunicationEntityFactory, DocumentEntityFactory


@pytest.fixture
def document_entity():
    yield DocumentEntityFactory(communication=CommunicationEntityFactory(comments=[]))


def test__add_document_to_user_and_organisation__document_added_to_org(uow, document_entity):
    document = uow.document.add(document_entity)
    user_id = "Test id"
    org_name = "Test organisation"

    uow.document.add_document_to_user_and_organisation(document.pk, user_id, org_name)
    user_docs = uow.document.get_user_document_entity_pks(user_id)
    organisation_docs = uow.document.get_organisation_document_entity_pks(org_name)

    assert len(organisation_docs) == 1
    assert document.pk in user_docs
    assert document.pk in organisation_docs


def test__get_organisation_document_entity_pks__doc_filtering(uow, document_entity):
    document = uow.document.add(document_entity)
    user_id = "Test id"
    org_name1 = "Test1 organisation"
    org_name2 = "Test2 organisation"

    uow.document.add_document_to_user_and_organisation(document.pk, user_id, org_name1)
    organisation_docs = uow.document.get_organisation_document_entity_pks(org_name2)

    assert len(organisation_docs) == 0
    assert document.pk not in organisation_docs
