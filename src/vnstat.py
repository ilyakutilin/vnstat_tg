import json
import subprocess
from datetime import date, datetime, timedelta
from enum import Enum

from src import exceptions as exc
from src import utils
from src.logging import configure_logging, log
from src.settings import settings

logger = configure_logging(__name__)


class Modifiers(Enum):
    day = "d"
    month = "m"


class VnStatData:
    def __init__(
        self,
        name: str,
        day: date,
        day_traffic: int,
        month: dict[str, int],
        month_traffic: int,
    ) -> None:
        self.name = name
        self.day = day
        self.day_traffic = day_traffic
        self.month = month
        self.month_traffic = month_traffic


@log
def __get_month_limit(date_: datetime = datetime.today()) -> int:
    """Returns the limit of months to request from vnstat."""
    todays_month = date_.month
    tomorrows_month = (date_ + timedelta(days=1)).month
    if tomorrows_month != todays_month:
        return 2
    return 1


@log
def _get_command(modifier: Modifiers, limit: int = 2) -> list[str]:
    return ["vnstat", "--json", modifier.value, str(limit)]


@log
def _get_command_result(command: list[str]) -> dict | None:
    try:
        # Run vnstat to get the data in JSON format
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            raise exc.CommandError(f"vnstat command {command} failed")

        # Parse the JSON output
        data = json.loads(result.stdout)
        return data
    except Exception as e:
        raise exc.FetchError(f"Failed to fetch vnstat data: {e}")


@log
def __get_interface(
    jsoned_interface_list: dict,
    target_interface: str = settings.INTERFACE_NAME,
) -> dict | None:
    if not jsoned_interface_list:
        raise exc.MissingInterfacesError(
            "vnstat data does not contain interfaces"
        )

    for interface in jsoned_interface_list:
        if interface.get("name") != target_interface:
            continue
        return interface

    raise exc.MissingInterfacesError(
        f"vnstat data does not contain interface {target_interface}"
    )


@log
def _get_jsoned_traffic_list(
    command_result: dict, target_interface: str = settings.INTERFACE_NAME
) -> dict | None:
    jsoned_inteface_list = utils.get_dict_value(command_result, "interfaces")
    interface_data = __get_interface(jsoned_inteface_list, target_interface)

    jsoned_traffic = utils.get_dict_value(interface_data, "traffic")
    if "day" in jsoned_traffic:
        return jsoned_traffic.get("day")
    elif "month" in jsoned_traffic:
        return jsoned_traffic.get("month")
    else:
        raise exc.NoDayOrMonthError(
            "vnstat data does not contain traffic "
            f"for interface {target_interface}"
        )


@log
def __validate_and_get_day(
    jsoned_traffic_date: dict, target_date: date = date.today()
) -> tuple[bool, date]:
    dt_date = date(
        year=utils.get_dict_value(jsoned_traffic_date, "year"),
        month=utils.get_dict_value(jsoned_traffic_date, "month"),
        day=utils.get_dict_value(jsoned_traffic_date, "day"),
    )
    return dt_date == target_date - timedelta(days=1), dt_date


@log
def __validate_and_get_month(
    jsoned_traffic_date: dict, target_date: date = date.today()
) -> tuple[bool, dict]:
    date_ = {
        "year": utils.get_dict_value(jsoned_traffic_date, "year"),
        "month": utils.get_dict_value(jsoned_traffic_date, "month"),
    }
    current_day = target_date.day
    if current_day != 1:
        return date_["month"] == target_date.month, date_
    current_month = target_date.month
    previous_month = 12 if current_month == 1 else current_month - 1
    return date_["month"] == previous_month, date_


@log
def __sum_traffic(traffic_element: dict) -> int:
    rx = utils.get_dict_value(traffic_element, "rx")
    tx = utils.get_dict_value(traffic_element, "tx")
    return rx + tx


@log
def _get_traffic_for_correct_period(
    jsoned_traffic_list: dict,
    day_or_month: Modifiers,
    target_date: date = date.today(),
) -> tuple[int | None, date | dict[str, int]] | None:
    for element in jsoned_traffic_list:
        jsoned_traffic_date = utils.get_dict_value(element, "date")
        if day_or_month == Modifiers.day:
            is_valid, period = __validate_and_get_day(
                jsoned_traffic_date, target_date
            )
        elif day_or_month == Modifiers.month:
            is_valid, period = __validate_and_get_month(
                jsoned_traffic_date, target_date
            )
        else:
            raise exc.InvalidModifierError(
                f"Only {Modifiers.day.value} and {Modifiers.month.value} "
                "are supported"
            )
        if is_valid:
            return __sum_traffic(element), period

    return None, period


@log
def _get_traffic_in_bytes(
    day_or_month: Modifiers, target_date: date = date.today()
) -> tuple[int | None, date | dict[str, int]] | None:
    day_command = _get_command(day_or_month)
    day_command_result = _get_command_result(day_command)
    jsoned_traffic_list = _get_jsoned_traffic_list(day_command_result)
    return _get_traffic_for_correct_period(
        jsoned_traffic_list, day_or_month, target_date
    )


@log
def get_traffic_data(
    service_name: str, target_date: date = date.today()
) -> VnStatData | None:
    try:
        day_traffic, day = _get_traffic_in_bytes(Modifiers.day, target_date)
        month_traffic, month = _get_traffic_in_bytes(
            Modifiers.month, target_date
        )
    except exc.InternalError as e:
        raise e

    return VnStatData(
        name=service_name,
        day=day,
        day_traffic=day_traffic,
        month=month,
        month_traffic=month_traffic,
    )
