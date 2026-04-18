import json
from http import HTTPStatus
from typing import Any, Optional

from fastapi import Form
from fastapi.exceptions import HTTPException
from pydantic import Json, ValidationError

from deps_documents.domain.entities import LabelEntityPk, ParsingFeature

__all__ = ["get_parsing_features", "get_label_ids", "parse_metadata"]


def get_parsing_features(
    parsing_features: Optional[Json] = Form(None, alias="parsingFeatures"),
) -> Optional[set[ParsingFeature]]:
    try:
        return {ParsingFeature(feature) for feature in parsing_features} if parsing_features else None
    except ValidationError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=e.errors())


def get_label_ids(
    label_ids: Optional[Json] = Form(None, alias="labelIds"),
) -> Optional[list[LabelEntityPk]]:
    try:
        return [LabelEntityPk(label) for label in label_ids] if label_ids else None
    except ValidationError as e:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail=e.errors())


def parse_metadata(
    metadata: Optional[str] = Form(None),
) -> Optional[dict[str, Any]]:
    if metadata is None or metadata == "":
        return None
    try:
        return json.loads(metadata)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=f"Invalid JSON in metadata field: {str(e)}",
        )
