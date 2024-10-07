import json
import subprocess
from collections.abc import Generator
from datetime import date, timedelta
from enum import Enum
from typing import Optional

import jmespath as jm

from src import exceptions as exc
from src import settings, utils
from src.log import configure_logging, log
from src.systemctl import get_service_status

logger = configure_logging(__name__)


class Modifiers(Enum):
    """Modifiers for day and month."""

    DAY = "day"
    MONTH = "month"


class VnStatData:
    """VnStat data object."""

    def __init__(
        self,
        *,
        system_name: str,
        service_status: Optional[str] = None,
        stat_date: date,
        day_traffic: Optional[int] = None,
        month_traffic: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        self.system_name = system_name
        self.service_status = service_status
        self.stat_date = stat_date
        self.day_traffic = day_traffic
        self.month_traffic = month_traffic
        self.error = error

    def __repr__(self) -> str:
        day_traffic = (
            f"{self.day_traffic:,}".replace(",", " ")
            if self.day_traffic
            else None
        )
        month_traffic = (
            f"{self.month_traffic:,}".replace(",", " ")
            if self.month_traffic
            else None
        )
        return (
            f"<VnStatData(system_name='{self.system_name}', "
            f"service_status='{self.service_status}', "
            f"stat_date={self.stat_date.isoformat()}, "
            f"day_traffic={day_traffic}, "
            f"month_traffic={month_traffic}, "
            f"error='{self.error}')>"
        )


@log
def _get_command_result(
    command: list[str] = settings.COMMAND,
) -> Optional[dict]:
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
) -> Optional[dict]:
    return jm.search(
        f"interfaces[?name=='{target_interface}'].traffic | [0]", vnstat_data
    )


@log
def __get_traffic_value(
    interface_traffic_data: Optional[dict],
    modifier: Modifiers,
    target_date: date,
) -> Optional[int]:
    day_part = (
        f" && date.day==`{target_date.day}`"
        if modifier == Modifiers.DAY
        else ""
    )
    rx_tx: Optional[list] = jm.search(
        f"{modifier.value}[?date.year==`{target_date.year}` "
        f"&& date.month==`{target_date.month}`{day_part}].[rx, tx] | [0]",
        interface_traffic_data,
    )
    if interface_traffic_data and not rx_tx:
        latest_date: list[Optional[int]] = jm.search(
            f"{modifier.value}[-1].date.[year, month, day]",
            interface_traffic_data,
        )
        date_obj = (
            date(*latest_date)
            if latest_date[-1]
            else utils.get_month_date_object(*latest_date[:-1])
        )
        slicer = (
            -3 if modifier == Modifiers.MONTH else len(date_obj.isoformat())
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
) -> Generator[Optional[int], Optional[int]]:
    interface_traffic_data = __get_interface_traffic_data(vnstat_data)
    return (
        __get_traffic_value(interface_traffic_data, modifier, target_date)
        for modifier in Modifiers
    )


@log
def get_traffic_data(
    system_name: str, target_date: date = date.today() - timedelta(days=1)
) -> Optional[VnStatData]:
    """Get traffic data from vnstat."""
    try:
        service_status = get_service_status()
        vnstat_data = _get_command_result()
        day_traffic, month_traffic = _get_traffic_in_bytes(
            vnstat_data, target_date
        )
    except exc.InternalError as e:
        return VnStatData(
            system_name=system_name,
            service_status=None,
            stat_date=target_date,
            error=str(e),
        )

    return VnStatData(
        system_name=system_name,
        service_status=service_status,
        stat_date=target_date,
        day_traffic=day_traffic,
        month_traffic=month_traffic,
    )


vn_sim = VnStatData(
    system_name="local",
    service_status="Vnstat service status: active",
    stat_date=date.today() - timedelta(days=1),
    day_traffic=1000000000,
    month_traffic=2000000000,
)

vn_sim_error = VnStatData(
    system_name="remote",
    service_status="Vnstat service status: seems to be inactive",
    stat_date=date.today() - timedelta(days=1),
    error="Simulated error",
)

if __name__ == "__main__":
    print(get_traffic_data("local", date.today() - timedelta(days=1)))
