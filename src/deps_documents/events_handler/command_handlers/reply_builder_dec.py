import logging
from functools import wraps
from typing import Any, Callable, Optional, Type, Union

from deps_message_flow.commands.consumer import CommandMessage
from deps_message_flow.messaging.common import IMessage

from deps_documents.domain.constants import ErrorType
from deps_documents.domain.exceptions import BusinessException

from .commands import AssignDocumentTypeReply, UpdateContainerDataReply
from .reply_builder import ParticipantReplyBuilder

__all__ = ["send_participant_reply"]

_logger = logging.getLogger(__name__)

CommandResult = list[IMessage]
CommandHandler = Callable[..., Optional[dict[str, Any]]]
WrappedHandler = Callable[..., CommandResult]
CommandWithError = Union[AssignDocumentTypeReply, UpdateContainerDataReply]


def send_participant_reply(reply: Type[CommandWithError]) -> Callable[[CommandHandler], WrappedHandler]:
    def dec_participant_reply(command_handler: CommandHandler) -> WrappedHandler:
        @wraps(command_handler)
        def wrapper_participant_reply(command: CommandMessage, *args, **kwargs) -> CommandResult:
            handler_result = invoke_handler(command, *args, **kwargs)
            log_result(command, handler_result)

            return [ParticipantReplyBuilder.with_success(reply(**handler_result) if handler_result else reply())]

        def invoke_handler(command: CommandMessage, *args, **kwargs) -> Optional[dict[str, Any]]:
            handler_result: Optional[dict[str, Any]]
            try:
                if handler_result := command_handler(command, *args, **kwargs):
                    if not isinstance(handler_result, dict):
                        raise RuntimeError("Provide appropriate dict from command handler for building reply.")

            except BusinessException as error:
                handler_result = {"error_type": ErrorType.BUSINESS, "error_message": str(error)}

            except Exception as error:
                handler_result = {"error_type": ErrorType.SYSTEM, "error_message": str(error)}

            return handler_result

        def log_result(command: CommandMessage, handler_result: Optional[dict[str, Any]]) -> None:
            if handler_result and handler_result.get("error_message"):
                _logger.error(
                    "[error_handler for %s] Error occured!\nReason: %s ",
                    command.command.__class__.__name__,
                    handler_result["error_message"],
                )
            else:
                _logger.info("[%s] with payload %s has been processed.", command.command.__class__.__name__, command.__dict__)

        return wrapper_participant_reply

    return dec_participant_reply
