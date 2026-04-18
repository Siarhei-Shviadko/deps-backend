from collections import namedtuple
from typing import Optional

from deps_message_flow.commands.common import Command

__all__ = ["FakeCommandProducer", "Commands"]


Commands = namedtuple("Commands", ("channel", "command", "reply_to"))


class FakeCommandProducer:
    def __init__(self) -> None:
        self._last_sended: Optional[Commands] = None

    @property
    def last_sended(self):
        return self._last_sended

    @last_sended.deleter
    def last_sended(self):
        self._last_sended = None

    def send(
        self,
        channel: str,
        command: Command,
        reply_to: str,
        **kwargs,
    ) -> None:
        self._last_sended = Commands(
            channel=channel,
            command=command,
            reply_to=reply_to,
        )
