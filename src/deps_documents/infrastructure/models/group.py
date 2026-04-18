from sqlalchemy import Boolean, Column, String, Table

from deps_documents.extras.datasource import metadata

group_table = Table(
    "group",
    metadata,
    Column("id", String, primary_key=True),
    Column("tenant_id", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("is_deleted", Boolean, default=False, nullable=False),
)
