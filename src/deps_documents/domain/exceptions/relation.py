from .common import AlreadyExistsError, ContextOperationError, NotFoundError


class RelationAlreadyExistsError(AlreadyExistsError):
    code = "relation_already_exists"

    def __init__(self, relation):
        message = f"Relation ({relation.type}, {relation.code}) already exists."
        super().__init__(message)


class RelationTypeAlreadyExistsError(AlreadyExistsError):
    code = "relation_type_already_exists"

    def __init__(self, relation_type=None):
        message = f"Relation type '{relation_type}' already exists."
        super().__init__(message)


class RelationNotFoundError(NotFoundError):
    code = "relation_not_found"

    def __init__(self, relation):
        if relation.code is None:
            message = f"Relations with type '{relation.type}' doesn't exist."
        else:
            message = f"Relation ({relation.type}, {relation.code}) does not exists."
        super().__init__(message)


class RelationTypeNotFoundError(NotFoundError):
    code = "relation_type_not_found"

    def __init__(self, relation_type=None):
        message = f"Relation type '{relation_type}' does not exists."
        super().__init__(message)


class RelationParentNotFoundError(NotFoundError):
    code = "relation_parent_not_found"

    def __init__(self, relation):
        message = f"Parent relation ({relation.type}, {relation.code}) does not exists."
        super().__init__(message)


class RelationChildrenNotFoundError(NotFoundError):
    code = "relation_children_not_found"

    def __init__(self, relation):
        message = f"Relation ({relation.type, relation.code}) has no children."
        super().__init__(message)


class RelationUpdatingError(ContextOperationError):
    code = "relation_updating_error"

    def __init__(self, relation, update_entity):
        exist_relation = f"({update_entity.code}, {update_entity.type})"
        message = f"Can't update {relation} to {exist_relation}. " f"{exist_relation} already exists."
        super().__init__(message)


class RelationTypeUpdatingError(ContextOperationError):
    code = "relation_type_updating_error"

    def __init__(self, relation_type, new_relation_type):
        message = f"Can't update ({relation_type}) to ({new_relation_type}). " f"({new_relation_type}) already exists."
        super().__init__(message)


class RelationFilterError(ContextOperationError):
    code = "relation_filter_error"

    def __init__(self):
        message = "Necessary at least one of argument. 'type' or 'code' of relation"
        super().__init__(message)
