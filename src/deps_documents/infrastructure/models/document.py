from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Sequence, String, Table
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from deps_documents.extras.datasource import metadata

document_table = Table(
    "document",
    metadata,
    Column("id", Integer, Sequence("document_id_seq"), primary_key=True, nullable=False),
    Column("source_code", String, ForeignKey("source.code")),
    Column("parent_id", Integer, ForeignKey("document.id", deferrable=True, ondelete="cascade")),
    Column("title", String),
    Column("state", String, default="NEW"),
    Column("file", JSONB),
    Column("files", JSONB),
    Column("document_type", String, nullable=True),
    Column("sub_type", String, nullable=True),
    Column("date", DateTime(timezone=True), default=datetime.utcnow, server_default=func.now()),
    Column("reviewer", String, ForeignKey("reviewer.id", ondelete="cascade"), nullable=True),
    Column("language", String, nullable=True),
    Column("engine", String, nullable=True),
    Column("llm_type", String, nullable=True),
    Column("scraped_api_number", String, nullable=True),
    Column("preview_documents", JSONB, nullable=True),
    Column("processing_documents", JSONB, nullable=True),
    Column("error_description", String, nullable=True),
    Column("error_in_state", String, nullable=True),
    Column("container_type", String, nullable=True),
    Column("container_metadata", JSONB, nullable=True),
    Column("assignment_status", String),
    Column("priority", String),
    Column("group_id", String, nullable=True),
    Column("processing_parameters", JSONB, nullable=True),
)

comment_table = Table(
    "comment",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("document_id", Integer, ForeignKey("document.id", ondelete="cascade"), nullable=False),
    Column("text", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=func.now()),
    Column("user_id", String),
)

document_log_table = Table(
    "document_log",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("document_id", Integer, ForeignKey("document.id", ondelete="cascade")),
    Column("action", String),
    Column("previous", String),
    Column("current", String),
    Column("created_at", DateTime(timezone=False), nullable=False, default=datetime.utcnow, server_default=func.now()),
    Column("actor", String),
)

user_has_document_table = Table(
    "user_has_document",
    metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="cascade")),
    Column("user_id", Integer),
)

organisation_has_document_table = Table(
    "organisation_has_document",
    metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="cascade")),
    Column("organisation_name", String),
)

document_metadata_table = Table(
    "document_metadata",
    metadata,
    Column("document_id", Integer, ForeignKey("document.id", ondelete="cascade"), primary_key=True),
    Column("metadata", JSONB, nullable=False, default=lambda: {}),  # noqa: WPS522
)
