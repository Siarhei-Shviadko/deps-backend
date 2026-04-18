from sqlalchemy import Column, String, Table

from deps_documents.extras.datasource import metadata

reviewer_table = Table(
    "reviewer",
    metadata,
    Column("id", String, primary_key=True),
    Column("email", String),
    Column("first_name", String),
    Column("last_name", String),
)
