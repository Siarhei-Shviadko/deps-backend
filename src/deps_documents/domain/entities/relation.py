from dataclasses import dataclass, field
from typing import Any, Dict, List, NewType, Optional

RelationType = NewType("RelationType", str)


@dataclass
class RelationEntity:
    type: str
    code: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    assigned_documents: List[int] = field(default_factory=list)
    parent_type: Optional[str] = None
    parent_code: Optional[str] = None
