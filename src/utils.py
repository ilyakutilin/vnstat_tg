import calendar
import json
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from src import settings
from src.log import configure_logging, log

if TYPE_CHECKING:
    from src.vnstat import VnStatData

logger = configure_logging(__name__)


@log
def bytes_to_gb(bytes_value: Optional[int] = None, bold: bool = False) -> str:
    """Converts bytes to gigabytes."""
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
    vnstat_data: "VnStatData", file_path: Path = settings.LOCAL_JSON_FILE_NAME
):
    """Save VnStat data to file."""
    vn_dict = vnstat_data.__dict__
    vn_dict["stat_date"] = vn_dict["stat_date"].isoformat()
    vn_json = json.dumps(vn_dict)
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(vn_json)


@log
def get_month_date_object(year: int, month: int) -> date:
    """Gets the date object from year and month."""
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)


if __name__ == "__main__":
    from src.vnstat import vn_sim

    save_vnstat_data_to_file(vn_sim)
