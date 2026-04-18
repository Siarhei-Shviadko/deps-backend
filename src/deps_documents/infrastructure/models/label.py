from sqlalchemy import Column, ForeignKey, Integer, String, Table

from deps_documents.extras.datasource import metadata

labels_table = Table(
    "labels",
    metadata,
    Column("label_id", Integer, ForeignKey("label.id", ondelete="cascade"), primary_key=True),
    Column("document_id", Integer, ForeignKey("document.id", ondelete="cascade"), primary_key=True),
)

label_table = Table(
    "label",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(32), nullable=False),  # noqa: WPS432
)

organisation_has_label_table = Table(
    "organisation_has_label",
    metadata,
    Column("label_id", Integer, ForeignKey("label.id", ondelete="cascade"), primary_key=True),
    Column("organisation_name", String, primary_key=True),
)
