import pytest

from deps_documents.domain.exceptions import PrimaryKeyError
from tests.factories import CommunicationEntityFactory, DocumentEntityFactory


@pytest.fixture
def document_entity():
    yield DocumentEntityFactory(communication=CommunicationEntityFactory(comments=[]))


def test__check_documents_for_organisation__document_exists__returns_true(uow, document_entity):
    document = uow.document.add(document_entity)
    user_id = "test_user_123"
    org_name = "deps-admins"

    uow.document.add_document_to_user_and_organisation(document.pk, user_id, org_name)
    uow.commit()

    result = uow.document.check_documents_for_organisation(organisation_entity_name=org_name, document_ids=[document.pk])

    assert result is True


def test__check_documents_for_organisation__with_multiple_documents__all_exist(uow):
    doc1 = uow.document.add(DocumentEntityFactory(communication=CommunicationEntityFactory(comments=[])))
    doc2 = uow.document.add(DocumentEntityFactory(communication=CommunicationEntityFactory(comments=[])))
    user_id = "test_user_456"
    org_name = "test-org"

    uow.document.add_document_to_user_and_organisation(doc1.pk, user_id, org_name)
    uow.document.add_document_to_user_and_organisation(doc2.pk, user_id, org_name)
    uow.commit()

    result = uow.document.check_documents_for_organisation(organisation_entity_name=org_name, document_ids=[doc1.pk, doc2.pk])

    assert result is True


def test__check_documents_for_organisation__with_missing_document__returns_false(uow, document_entity):
    document = uow.document.add(document_entity)
    user_id = "test_user_789"
    org_name = "test-org-2"

    uow.document.add_document_to_user_and_organisation(document.pk, user_id, org_name)
    uow.commit()

    fake_doc_id = "999999"

    result = uow.document.check_documents_for_organisation(
        organisation_entity_name=org_name, document_ids=[document.pk, fake_doc_id]
    )

    assert result is False


def test__check_documents_for_organisation__with_invalid_hex_id__raises_error(uow, document_entity):
    document = uow.document.add(document_entity)
    user_id = "test_user_999"
    org_name = "test-org-3"

    uow.document.add_document_to_user_and_organisation(document.pk, user_id, org_name)
    uow.commit()

    with pytest.raises(PrimaryKeyError, match=r"Could not cast ID to int"):
        uow.document.check_documents_for_organisation(
            organisation_entity_name=org_name, document_ids=["3dc399920fa84a66ae1d67412f6f363e"]
        )
