from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["UnassignReviewer"]


@dataclass
class UnassignReviewer(Command):
    document_id: str
