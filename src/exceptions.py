from src import tg
from src.logging import configure_logging, log

logger = configure_logging(__name__)


class InternalError(Exception):
    pass


class CommandError(InternalError):
    pass


class FetchError(InternalError):
    pass


class InternalKeyError(InternalError):
    pass


class MissingInterfacesError(InternalError):
    pass


class MissingTrafficError(InternalError):
    pass


class NoDayOrMonthError(InternalError):
    pass


class InvalidModifierError(InternalError):
    pass


class TelegramError(InternalError):
    pass


@log
def handle_exception(exception: Exception, re_raise: bool = False) -> None:
    logger.exception(exception)
    tg.send_telegram_message(
        f"An exception was raised in your vnstat monitor: {str(exception)}"
    )
    if re_raise:
        raise exception
