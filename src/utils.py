import json
from pathlib import Path
from typing import TYPE_CHECKING

from src.exceptions import InternalKeyError
from src.logging import configure_logging, log
from src.settings import settings

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
def bytes_to_gb(bytes_value: int | None) -> str:
    if not bytes_value:
        return "No data"
    gb_value = bytes_value / (1024**3)
    formatted_value = f"{gb_value:.1f}".rstrip("0").rstrip(".") + " GB"
    return formatted_value


@log
def _save_data_to_file(data: str, file_path: str):
    with open(file_path, "w") as file:
        file.write(data)


@log
def save_vnstat_data_to_file(
    vnstat_data: "VnStatData", file_path: Path = settings.LOCAL_FILE_NAME
):
    vn_dict = vnstat_data.__dict__
    vn_dict["day"] = vn_dict["day"].isoformat()
    vn_json = json.dumps(vn_dict)
    _save_data_to_file(vn_json, file_path)
