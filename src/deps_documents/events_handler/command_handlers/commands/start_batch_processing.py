from dataclasses import dataclass

from deps_message_flow.commands.common import Command

__all__ = ["StartBatchProcessing"]

DocumentId = str


@dataclass
class StartBatchProcessing(Command):
    documents: list[DocumentId]
