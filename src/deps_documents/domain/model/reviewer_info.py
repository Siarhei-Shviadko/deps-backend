from typing import TypedDict

__all__ = ["ReviewerInfo"]


class ReviewerInfo(TypedDict):
    subject: str
    email: str
    first_name: str
    last_name: str
