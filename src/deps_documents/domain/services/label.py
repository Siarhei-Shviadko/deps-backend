from typing import Callable, List

from deps_documents.domain.dtos import LabelListFilterObject
from deps_documents.domain.entities import LabelEntity
from deps_documents.domain.interfaces import IDocumentUnitOfWork, ILabelService


class LabelService(ILabelService):
    def __init__(self, uow: Callable[..., IDocumentUnitOfWork]):
        self._uow = uow

    def create(self, label_entity: LabelEntity) -> LabelEntity:
        with self._uow() as uow:
            label_entity = uow.label.add(label_entity)
            uow.commit()
        return label_entity

    def get_list(self, options: LabelListFilterObject) -> List[LabelEntity]:
        with self._uow() as uow:
            label_list = uow.label.get_list(options)
            uow.commit()
        return label_list
