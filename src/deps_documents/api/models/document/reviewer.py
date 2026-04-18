from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from deps_documents.domain.entities import Reviewer
from deps_documents.infrastructure.access_management.context_vars import user


class ReviewerModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str = Field(...)
    email: Optional[str] = Field(None)
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")

    def to_domain(self):
        return Reviewer(
            id=self.id,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
        )

    @classmethod
    def from_current_user(cls) -> Reviewer:
        current_user = user.get(None)
        return (
            ReviewerModel(
                id=current_user["subject"],
                email=current_user.get("email"),
                first_name=current_user.get("first_name"),
                last_name=current_user.get("last_name"),
            ).to_domain()
            if current_user
            else None
        )
