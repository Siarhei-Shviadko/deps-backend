from deps_documents.domain.entities import RelationEntity


def build_relation_entity(relation_in_db, assigned_documents=None) -> RelationEntity:
    return RelationEntity(
        type=relation_in_db.type,
        code=relation_in_db.code,
        metadata=relation_in_db.metadata,
        assigned_documents=[] if assigned_documents is None else assigned_documents,
        parent_type=relation_in_db.parent_type,
        parent_code=relation_in_db.parent_code,
    )
