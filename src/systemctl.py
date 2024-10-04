import builtins
import keyword
import re
import subprocess
from datetime import datetime

from src.log import log

PROPERTIES = [
    "Id",
    "LoadState",
    "ActiveState",
    "SubState",
    "UnitFileState",
    "ActiveEnterTimestamp",
    "InactiveEnterTimestamp",
]

COMMAND = [
    "systemctl",
    "show",
    "vnstat",
    f"--property={(','.join(PROPERTIES))}",
]

ERROR_OUTPUT_LIMIT = 100


class SystemctlStatus:
    def __init__(self, param_list):
        for param in param_list:
            key, value = param.split("=", 1)

            key = self.pascal_to_snake_case(key)

            if self.is_keyword_or_builtin(key):
                key = f"{key}_"
            if "timestamp" in key:
                value = self.parse_timestamp(value)

            setattr(self, key, value if value else None)

    def pascal_to_snake_case(self, name):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def is_keyword_or_builtin(self, word):
        return keyword.iskeyword(word) or word in dir(builtins)

    def parse_timestamp(self, timestamp_str):
        try:
            return datetime.strptime(timestamp_str, "%a %Y-%m-%d %H:%M:%S %Z")
        except ValueError:
            return None

    def format_value(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return repr(value)

    def __repr__(self):
        attrs = ", ".join(
            f"{key}={self.format_value(value)}"
            for key, value in self.__dict__.items()
        )
        return f"<ParamParser({attrs})>"


@log
def _parse_status(status: SystemctlStatus) -> str:
    try:
        if status.active_state == "active" and status.active_enter_timestamp:
            formatted_time = status.active_enter_timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            since = f" since {formatted_time}"
        elif (
            status.active_state == "inactive"
            and status.inactive_enter_timestamp
        ):
            formatted_time = status.inactive_enter_timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            since = f" since {formatted_time}"
        else:
            since = ""
        return (
            f"{status.id_} is <b>{status.load_state}</b>, "
            f"<b>{status.active_state}</b> ({status.sub_state}){since}, "
            f"unit is <b>{status.unit_file_state}</b>"
        )
    except AttributeError as e:
        return f"vnstat.service: could not parse status: {e} "


@log
def get_service_status() -> str | None:
    try:
        res = subprocess.run(COMMAND, capture_output=True, text=True)
    except Exception as e:
        return (
            "vnstat.service: an error occurred while trying "
            f"to fetch the status: '{e}'"
        )

    if res.stderr:
        error_msg = res.stderr.strip().strip("\n")[:ERROR_OUTPUT_LIMIT]
        return f"vnstat.service: status <b>unknown</b>: {error_msg}"

    if res.stdout:
        params = res.stdout.strip().split("\n")
        status = SystemctlStatus(params)
        return _parse_status(status)

    return None


if __name__ == "__main__":
    print(get_service_status())
