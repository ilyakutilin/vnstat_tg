from src.log import configure_logging, log

logger = configure_logging(__name__)


class InternalError(Exception):
    pass


class CommandError(InternalError):
    pass


class FetchError(InternalError):
    pass


class InternalKeyError(InternalError):
    pass


class MissingTargetDateError(InternalError):
    pass


class MissingLocalFileError(InternalError):
    pass


class JSONDecodeError(InternalError):
    pass


class TelegramError(InternalError):
    pass


class SSHError(InternalError):
    pass


class SCPError(InternalError):
    pass


@log
def handle_exception(
    exception: Exception, re_raise: bool = True, send_tg: bool = True
) -> None:
    from src.tg import send_telegram_message

    logger.exception(exception)
    if send_tg:
        send_telegram_message(
            f"An exception was raised in your vnstat monitor: {str(exception)}"
        )
    if re_raise:
        raise exception
