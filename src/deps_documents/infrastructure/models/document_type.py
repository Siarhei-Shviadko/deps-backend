from sqlalchemy import Column, String, Table

from deps_documents.extras.datasource import metadata

document_type_table = Table(
    "type",
    metadata,
    Column("id", String, primary_key=True),
    Column("tenant", String, primary_key=True),
    Column("name", String, index=True),
)
