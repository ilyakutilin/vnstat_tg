import json
import subprocess
from datetime import date, timedelta
from enum import Enum

import jmespath as jm

from src import exceptions as exc
from src import settings, utils
from src.log import configure_logging, log

logger = configure_logging(__name__)


class Modifiers(Enum):
    day = "day"
    month = "month"


class VnStatData:
    def __init__(
        self,
        *,
        service_name: str,
        stat_date: date,
        day_traffic: int | None = None,
        month_traffic: int | None = None,
        error: str | None = None,
    ) -> None:
        self.name = service_name
        self.stat_date = stat_date
        self.day_traffic = day_traffic
        self.month_traffic = month_traffic
        self.error = error

    def __repr__(self) -> str:
        return (
            f"<VnStatData(name='{self.name}', "
            f"stat_date={self.stat_date.isoformat()}, "
            f"day_traffic={self.day_traffic}, "
            f"month_traffic={self.month_traffic}), "
            f"error='{self.error}')>"
        )


@log
def _get_command_result(
    command: list[str] = settings.COMMAND,
) -> dict | None:
    try:
        raw_json = subprocess.run(
            command, capture_output=True, text=True, check=True
        )
        result = json.loads(raw_json.stdout.strip("\n"))
    except subprocess.CalledProcessError as e:
        stdout = (
            f", stdout: `{e.stdout.strip()}`"
            if e.stdout and e.stdout != e.output
            else ""
        )
        stderr = f", stderr: `{e.stderr.strip()}`" if e.stderr else ""
        raise exc.CommandError(
            f"{settings.NO_DATA}: Error running command "
            f"`{' '.join(e.cmd)}`: returncode: {e.returncode}, "
            f"output: `{e.output.strip()}`{stdout}{stderr}"
        )
    except json.JSONDecodeError as e:
        raise exc.JSONDecodeError(f"Failed to parse data: {e}")
    except Exception as e:
        raise exc.FetchError(f"Failed to fetch data: {e}")
    return result


@log
def __get_interface_traffic_data(
    vnstat_data: dict,
    target_interface: str = settings.INTERFACE_NAME,
) -> dict | None:
    return jm.search(
        f"interfaces[?name=='{target_interface}'].traffic | [0]", vnstat_data
    )


@log
def __get_traffic_value(
    interface_traffic_data: dict | None, modifier: Modifiers, target_date: date
) -> int | None:
    day_part = (
        f" && date.day==`{target_date.day}`"
        if modifier == Modifiers.day
        else ""
    )
    rx_tx: list | None = jm.search(
        f"{modifier.value}[?date.year==`{target_date.year}` "
        f"&& date.month==`{target_date.month}`{day_part}].[rx, tx] | [0]",
        interface_traffic_data,
    )
    if interface_traffic_data and not rx_tx:
        latest_date: list[int | None] = jm.search(
            f"{modifier.value}[-1].date.[year, month, day]",
            interface_traffic_data,
        )
        date_obj = (
            date(*latest_date)
            if latest_date[-1]
            else utils.get_month_date_object(*latest_date[:-1])
        )
        slicer = (
            -3 if modifier == Modifiers.month else len(date_obj.isoformat())
        )

        raise exc.MissingTargetDateError(
            f"Target date {target_date} not found in traffic data. "
            f"Latest available {modifier.value} is "
            f"{date_obj.isoformat()[:slicer]}. "
            "Please check if the vnstat service is running."
        )
    return sum(rx_tx) if rx_tx else None


@log
def _get_traffic_in_bytes(
    vnstat_data: dict, target_date: date
) -> tuple[int | None, int | None]:
    interface_traffic_data = __get_interface_traffic_data(vnstat_data)
    return tuple(
        [
            __get_traffic_value(interface_traffic_data, modifier, target_date)
            for modifier in Modifiers
        ]
    )


@log
def get_traffic_data(
    service_name: str, target_date: date = date.today() - timedelta(days=1)
) -> VnStatData | None:
    try:
        vnstat_data = _get_command_result()
        day_traffic, month_traffic = _get_traffic_in_bytes(
            vnstat_data, target_date
        )
    except exc.InternalError as e:
        return VnStatData(
            service_name=service_name,
            stat_date=target_date,
            error=str(e),
        )

    return VnStatData(
        service_name=service_name,
        stat_date=target_date,
        day_traffic=day_traffic,
        month_traffic=month_traffic,
    )


vn_sim = VnStatData(
    service_name="local",
    stat_date=date.today() - timedelta(days=1),
    day_traffic=1000000000,
    month_traffic=2000000000,
)

vn_sim_error = VnStatData(
    service_name="remote",
    stat_date=date.today() - timedelta(days=1),
    error="Simulated error",
)

if __name__ == "__main__":
    print(get_traffic_data("local", date.today() - timedelta(days=3)))
