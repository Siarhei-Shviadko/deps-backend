from typing import Optional

from deps_documents.extras.value_objects import UserValueObject
from deps_documents.infrastructure.access_management.context_vars import user


class CurrentUserMixin:
    @property
    def current_user(self) -> Optional[UserValueObject]:
        user_credentials = user.get(None)
        if user_credentials is not None:
            return UserValueObject(**user_credentials)

        return user_credentials
