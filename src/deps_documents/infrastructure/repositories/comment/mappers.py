from typing import Any, Dict, Union

from sqlalchemy.engine import RowProxy

from deps_documents.domain.entities import CommentEntity


def build_comment_entity(comment_obj: Union[Dict[str, Any], RowProxy]) -> CommentEntity:
    return CommentEntity(text=comment_obj["text"], created_at=comment_obj["created_at"], created_by=comment_obj["user_id"])


def build_dict_from_comment_entity(comment: CommentEntity) -> Dict[str, Any]:
    return {
        "text": comment.text,
        "created_at": comment.created_at,
        "user_id": comment.created_by,
    }
