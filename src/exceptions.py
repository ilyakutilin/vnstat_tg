from src.log import configure_logging, log

logger = configure_logging(__name__)


class InternalError(Exception):
    """Base class for the project exceptions."""


class CommandError(InternalError):
    """Raised when the system command fails."""


class FetchError(InternalError):
    """Raised when the output from the system command cannot be parsed."""


class MissingTargetDateError(InternalError):
    """Raised when the target date is missing in the Vnstat data."""


class MissingLocalFileError(InternalError):
    """Raised when the local file cannot be found."""


class JSONDecodeError(InternalError):
    """Raised when the JSON data cannot be parsed."""


class TelegramError(InternalError):
    """Raised when the Telegram message cannot be sent."""


class SSHError(InternalError):
    """Raised when the SSH connection cannot be established."""


class SCPError(InternalError):
    """Raised when the SSH connection cannot be established."""


@log
def handle_exception(
    exception: Exception, re_raise: bool = True, send_tg: bool = True
) -> None:
    """
    Log the exception, (optionally) send Telegram message and re-raise."""
    from src.tg import send_telegram_message

    logger.exception(exception)
    if send_tg:
        send_telegram_message(
            f"An exception was raised in your vnstat monitor: {str(exception)}"
        )
    if re_raise:
        raise exception
