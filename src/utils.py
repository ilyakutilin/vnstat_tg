import calendar
import json
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

from src import settings
from src.exceptions import InternalKeyError
from src.log import configure_logging, log

if TYPE_CHECKING:
    from src.vnstat import VnStatData

logger = configure_logging(__name__)


@log
def get_dict_value(dict_: dict, key: str):
    try:
        return dict_[key]
    except KeyError:
        message = f"KeyError: no key {key} in dict {dict_}"
        logger.error(message)
        raise InternalKeyError(message)


@log
def bytes_to_gb(bytes_value: int | None = None, bold: bool = False) -> str:
    if not bytes_value:
        return "No data"
    gb_value = bytes_value / (1024**3)
    gb_value_stripped = f"{gb_value:.1f}".rstrip("0").rstrip(".")
    bold_tag_open = "<b>" if bold else ""
    bold_tag_close = "</b>" if bold else ""
    formatted_value = f"{bold_tag_open}{gb_value_stripped}{bold_tag_close} GB"
    return formatted_value


@log
def save_vnstat_data_to_file(
    vnstat_data: "VnStatData", file_path: Path = settings.LOCAL_FILE_NAME
):
    vn_dict = vnstat_data.__dict__
    vn_dict["stat_date"] = vn_dict["stat_date"].isoformat()
    vn_json = json.dumps(vn_dict)
    with open(file_path, "w") as file:
        file.write(vn_json)


@log
def get_month_date_object(year: int, month: int) -> date:
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)


if __name__ == "__main__":
    from src.vnstat import vn_sim

    save_vnstat_data_to_file(vn_sim)
