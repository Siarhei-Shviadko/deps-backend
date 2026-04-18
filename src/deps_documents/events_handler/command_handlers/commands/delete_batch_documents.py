from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["DeleteBatchDocument"]

DocumentId = str


@dataclass
class DeleteBatchDocument(Command):
    document: DocumentId
