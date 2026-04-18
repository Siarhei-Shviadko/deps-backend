from typing import Optional

from pydantic import BaseModel, Field

from deps_documents.api.models.strict_str import StrictStr


class ExtractionParams(BaseModel):
    ocr: bool = False
    tables: bool = False
    ner: bool = False
    ocr_engine: Optional[str] = Field(None, alias="ocrEngine")
    table_detection_engine: Optional[str] = Field(None, alias="tableDetectionEngine")
    language: Optional[str] = None
    ner_entities: list[str] = Field(default_factory=list, alias="nerEntities")


class DocumentExtractModel(BaseModel):
    document_ids: list[StrictStr] = Field(..., alias="documentIds", min_items=1)
    engine: str = Field(None, alias="engineName")
