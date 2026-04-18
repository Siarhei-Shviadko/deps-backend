from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from deps_documents.domain.entities import BlobFile


@dataclass
class PreprocessResultEntity:
    entity_type: str
    preview: List[BlobFile] = field(default_factory=list)
    processing: List[BlobFile] = field(default_factory=list)
    meta: Optional[Dict[str, Any]] = None
