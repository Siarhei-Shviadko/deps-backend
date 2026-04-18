from dataclasses import dataclass


@dataclass
class DocumentTypeEntity:
    id: str
    tenant: str
    name: str
