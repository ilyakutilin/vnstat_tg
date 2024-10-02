import locale
from http import HTTPStatus

import requests

from src import exceptions as exc
from src import utils
from src.log import configure_logging, log
from src.settings import settings
from src.vnstat import VnStatData

locale.setlocale(locale.LC_TIME, "en_US.UTF-8")

logger = configure_logging(__name__)


@log
def get_msg_for_service(vn_obj: VnStatData) -> str:
    day_traffic = utils.bytes_to_gb(vn_obj.day_traffic)
    month_traffic = utils.bytes_to_gb(vn_obj.month_traffic)
    return (
        f"<b>{vn_obj.name}</b>:\n"
        f"Yesterday, {vn_obj.day}: {day_traffic}\n"
        f"Cumulative for {vn_obj.month}: {month_traffic}\n\n"
    )


@log
def get_final_msg(*vnstat_objects: VnStatData) -> str:
    message = ""
    day_traffic = 0
    month_traffic = 0
    for vn_obj in vnstat_objects:
        message += get_msg_for_service(vn_obj)
        if vn_obj.day_traffic:
            day_traffic += vn_obj.day_traffic
        if vn_obj.month_traffic:
            month_traffic += vn_obj.month_traffic

    message += (
        "Total for all services:\n"
        f"Yesterday: {utils.bytes_to_gb(day_traffic)}\n"
        f"Cumulative: {utils.bytes_to_gb(month_traffic)}\n\n"
    )
    return message


@log
def send_telegram_message(
    message: str,
    telegram_bot_token: str = settings.TELEGRAM_BOT_TOKEN,
    telegram_chat_id: str = settings.TELEGRAM_CHAT_ID,
) -> None:

    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {"chat_id": telegram_chat_id, "text": message}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == HTTPStatus.OK:
            logger.info("Message sent successfully.")
        else:
            logger.error(
                f"Failed to send message. Status code: {response.status_code}"
            )
    except Exception as e:
        raise exc.TelegramError(f"Error sending Telegram message: {e}")
