from datetime import date
from report.filter import in_range


def test_middle_day_is_in_range():
    assert in_range(date(2024, 1, 15), date(2024, 1, 1), date(2024, 1, 31))
