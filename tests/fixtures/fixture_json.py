import json
from datetime import date, timedelta
from unittest.mock import Mock

import pytest
from dateutil.relativedelta import relativedelta


class DayMonth:
    def __init__(self, current_date: date, previous_date: date = None):
        self.today = current_date
        self.yesterday = (
            previous_date
            if previous_date
            else current_date - timedelta(days=1)
        )
        self.last_month = current_date - relativedelta(months=1)


def get_day_dict(dm: DayMonth):
    return {
        "vnstatversion": "2.6",
        "jsonversion": "2",
        "interfaces": [
            {
                "name": "eth0",
                "alias": "",
                "created": {"date": {"year": 2024, "month": 8, "day": 20}},
                "updated": {
                    "date": {
                        "year": dm.today.year,
                        "month": dm.today.month,
                        "day": dm.today.day,
                    },
                    "time": {"hour": 9, "minute": 40},
                },
                "traffic": {
                    "total": {"rx": 242920913679, "tx": 192091433958},
                    "day": [
                        {
                            "id": 29,
                            "date": {
                                "year": dm.yesterday.year,
                                "month": dm.yesterday.month,
                                "day": dm.yesterday.day,
                            },
                            "rx": 5094408961,
                            "tx": 3151798436,
                        },
                        {
                            "id": 30,
                            "date": {
                                "year": dm.today.year,
                                "month": dm.today.month,
                                "day": dm.today.day,
                            },
                            "rx": 1743913561,
                            "tx": 862805062,
                        },
                    ],
                },
            }
        ],
    }


def get_month_dict(dm: DayMonth):
    return {
        "vnstatversion": "2.6",
        "jsonversion": "2",
        "interfaces": [
            {
                "name": "eth0",
                "alias": "",
                "created": {"date": {"year": 2024, "month": 8, "day": 30}},
                "updated": {
                    "date": {
                        "year": dm.today.year,
                        "month": dm.today.month,
                        "day": dm.today.day,
                    },
                    "time": {"hour": 11, "minute": 5},
                },
                "traffic": {
                    "total": {"rx": 243177358338, "tx": 192225754382},
                    "month": [
                        {
                            "id": 2,
                            "date": {
                                "year": dm.last_month.year,
                                "month": dm.last_month.month,
                            },
                            "rx": 7821185928,
                            "tx": 5401883104,
                        },
                        {
                            "id": 3,
                            "date": {
                                "year": dm.today.year,
                                "month": dm.today.month,
                            },
                            "rx": 235356172410,
                            "tx": 186823871278,
                        },
                    ],
                },
            }
        ],
    }


@pytest.fixture(
    params=[
        (date(2024, 9, 12),),
        (date(2024, 9, 1),),
        (date(2024, 1, 1),),
        (date(2024, 9, 12), date(2024, 9, 10)),
    ],
    ids=[
        "general_case",
        "first_day_of_the_month",
        "first_day_of_the_year",
        "missing_yesterday",
    ],
)
def simulated_vnstat_data(request):
    dm = DayMonth(*request.param)
    day_json = json.dumps(get_day_dict(dm))
    month_json = json.dumps(get_month_dict(dm))
    return (day_json, month_json)


@pytest.fixture
def mock_subprocess_run(mocker, simulated_vnstat_data):
    def side_effect(command, *args, **kwargs):
        mock_result = Mock()
        mock_result.returncode = 0
        if "d" in command:
            mock_result.stdout = simulated_vnstat_data[0]
        elif "m" in command:
            mock_result.stdout = simulated_vnstat_data[1]
        return mock_result

    mocker.patch("subprocess.run", side_effect=side_effect)


@pytest.fixture
def mock_failed_subprocess_run(mocker):
    mock_result = Mock()
    mock_result.returncode = 1

    mocker.patch("subprocess.run", return_value=mock_result)
