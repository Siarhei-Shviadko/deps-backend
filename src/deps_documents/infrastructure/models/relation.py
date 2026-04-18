from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func, text

from deps_documents.extras.datasource import metadata

relation_table = Table(
    "relation",
    metadata,
    Column(
        "type",
        ForeignKey("relation_type.type", onupdate="CASCADE", ondelete="CASCADE", name="fk_relation_type"),
        primary_key=True,
    ),
    Column("code", String, primary_key=True),
    Column("created", DateTime(timezone=False), nullable=False, default=datetime.utcnow, server_default=func.now()),
    Column("updated", DateTime(timezone=False), nullable=False, default=datetime.utcnow, server_default=func.now()),
    Column("metadata", JSONB, nullable=False, default=dict, server_default=text("'{}'::jsonb")),  # noqa: P103
    Column("parent_type", String),
    Column("parent_code", String),
    ForeignKeyConstraint(
        columns=("parent_type", "parent_code"),
        refcolumns=("relation.type", "relation.code"),
        name="fk_parent_type_code",
        ondelete="CASCADE",
        onupdate="CASCADE",
    ),
)

document_relation_through_table = Table(
    "document_relation_through",
    metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="CASCADE", onupdate="CASCADE", name="fk_document")),
    Column("relation_type", String),
    Column("relation_code", String),
    ForeignKeyConstraint(
        columns=("relation_type", "relation_code"),
        refcolumns=("relation.type", "relation.code"),
        name="fk_relation_type_code",
        ondelete="CASCADE",
        onupdate="CASCADE",
    ),
    UniqueConstraint("document_id", "relation_type", "relation_code", name="document_relation_uniqkey"),
)

relation_type_table = Table(
    "relation_type",
    metadata,
    Column("type", String, primary_key=True),
)
