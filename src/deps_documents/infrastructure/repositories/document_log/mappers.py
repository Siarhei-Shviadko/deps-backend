from datetime import datetime, timezone
from typing import Any, Dict, Union

from sqlalchemy.engine import RowProxy

from deps_documents.domain.constants import ActorEnum, DocumentLogEnum
from deps_documents.domain.entities.document import DocumentLogEntity
from deps_documents.infrastructure.repositories.helpers import cast_to_db_pk


def build_dict_from_entity(doc_log_entity: DocumentLogEntity) -> Dict[str, Any]:
    return {
        "action": doc_log_entity.action.value,
        "previous": doc_log_entity.previous,
        "current": doc_log_entity.current,
        "created_at": doc_log_entity.created_at or datetime.now(tz=timezone.utc),
        "actor": doc_log_entity.actor and doc_log_entity.actor.value,
        "document_id": cast_to_db_pk(doc_log_entity.document_id),
    }


def build_document_log_entity(doc_log_raw: Union[Dict[str, Any], RowProxy]) -> DocumentLogEntity:
    return DocumentLogEntity(
        pk=doc_log_raw["id"],
        action=DocumentLogEnum(doc_log_raw["action"]),
        previous=doc_log_raw["previous"],
        current=doc_log_raw["current"],
        created_at=doc_log_raw["created_at"],
        actor=doc_log_raw["actor"] and ActorEnum(doc_log_raw["actor"]),
        document_id=doc_log_raw["document_id"],
    )
