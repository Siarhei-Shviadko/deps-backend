import pytest

from deps_documents.domain.entities import CommentEntity
from deps_documents.domain.exceptions import DocumentNotFoundError
from tests.factories import CommentEntityFactory, DocumentEntityFactory


class TestCaseCommentEntityRepository:
    def test_add_comment__document_exist__return_comment(self, uow):
        document = uow.document.add(DocumentEntityFactory())

        response = uow.comment.add(comment_entity=CommentEntityFactory(), document_entity_pk=document.pk)

        assert isinstance(response, CommentEntity)

    def test_add_comment__document_exist__add_comment(self, uow):
        document = uow.document.add(DocumentEntityFactory())
        comment = CommentEntityFactory()

        uow.comment.add(comment_entity=comment, document_entity_pk=document.pk)

        updated_document = uow.document.get(document.pk)

        assert len(updated_document.communication.comments) == 1

    def test_add_comment__document_not_exist__raise_document_not_found(self, uow):
        with pytest.raises(DocumentNotFoundError):
            uow.comment.add(comment_entity=CommentEntityFactory(), document_entity_pk="1")
