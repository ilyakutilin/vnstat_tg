import json
from datetime import date, timedelta

import pytest

from src import exceptions as exc
from src.vnstat import get_traffic_data


def test_parse_json(simulated_vnstat_data, mock_subprocess_run):
    json_day_data = json.loads(simulated_vnstat_data[0])
    date_dict = json_day_data["interfaces"][0]["updated"]["date"]
    simulated_today_date = date(
        date_dict["year"], date_dict["month"], date_dict["day"]
    )
    target_yesterday_date = simulated_today_date - timedelta(days=1)
    traffic_data = get_traffic_data("test_service", simulated_today_date)
    assert traffic_data.name == "test_service"
    assert traffic_data.day == target_yesterday_date
    target_day_traffic = (
        5094408961 + 3151798436
        if target_yesterday_date.day
        in [
            item["date"]["day"]
            for item in json_day_data["interfaces"][0]["traffic"]["day"]
        ]
        else None
    )
    assert traffic_data.day_traffic == target_day_traffic
    target_month = target_yesterday_date
    assert traffic_data.month == {
        "year": target_month.year,
        "month": target_month.month,
    }
    target_month_traffic = (
        235356172410 + 186823871278
        if target_month.month == simulated_today_date.month
        else 7821185928 + 5401883104
    )
    assert traffic_data.month_traffic == target_month_traffic


def test_json_parsing_fails(mock_failed_subprocess_run):
    with pytest.raises(exc.FetchError) as excinfo:
        get_traffic_data("test_service")
    assert "Failed to fetch vnstat data" in str(excinfo.value)
