from typing import Any, Dict

from sqlalchemy.engine import RowProxy

from deps_documents.domain.entities.label import LabelEntity, LabelEntityPk


def build_dict_from_entity(label_entity: LabelEntity) -> Dict[str, Any]:
    label = {"name": label_entity.name}
    if label_entity.pk:
        label["id"] = label_entity.pk

    return label


def convert_row_proxy_to_label_entity(label_entity: RowProxy) -> LabelEntity:
    return LabelEntity(
        pk=LabelEntityPk(str(label_entity["label_id"])),
        name=label_entity["label_name"],
    )


def build_label_entity(label_obj: RowProxy) -> LabelEntity:
    return LabelEntity(
        pk=LabelEntityPk(str(label_obj["id"])),
        name=label_obj["name"],
    )
