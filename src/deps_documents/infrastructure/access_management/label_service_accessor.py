from typing import List

from deps_documents.domain.dtos import LabelListFilterObject
from deps_documents.domain.entities import LabelEntity
from deps_documents.domain.interfaces import ILabelService
from deps_documents.infrastructure.access_management.label_access_manager import (
    ILabelServiceAccessManager,
)


class LabelServiceAccessor(ILabelService):
    def __init__(self, label_service: ILabelService, label_access_manager: ILabelServiceAccessManager):
        self._label_service = label_service
        self._label_access_manager = label_access_manager

    def create(self, label_entity: LabelEntity) -> LabelEntity:
        self._label_access_manager.check_uniqueness(label_entity.name)
        label = self._label_service.create(label_entity)
        self._label_access_manager.add_permissions_after_creating(label.pk)

        return label

    def get_list(self, options: LabelListFilterObject) -> List[LabelEntity]:
        self._label_access_manager.patch_filter(options)

        return self._label_service.get_list(options)
