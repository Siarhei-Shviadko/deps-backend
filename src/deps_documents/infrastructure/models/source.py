from sqlalchemy import Column, String, Table

from deps_documents.extras.datasource import metadata

source_table = Table(
    "source",
    metadata,
    Column("code", String(32), primary_key=True, nullable=False),  # noqa: WPS432
    Column("title", String(128), nullable=False),  # noqa: WPS432
)
