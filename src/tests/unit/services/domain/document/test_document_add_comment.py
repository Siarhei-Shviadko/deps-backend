from deps_documents.domain.entities import CommentEntity
from tests.factories.document_entity import CommentEntityFactory


class TestDocumentAddCommentUseCase:
    def test_execute__configs_exist__resp_value_not_empty(self, domain_services, uow):
        comment_entity = CommentEntityFactory()
        uow.comment.add.return_value = comment_entity

        result = domain_services.document().add_comment(comment_entity=comment_entity, document_entity_pk="1")

        assert isinstance(result, CommentEntity)
