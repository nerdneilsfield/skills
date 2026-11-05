from datetime import date


def in_range(day: date, start: date, end: date) -> bool:
    # BUG: end is exclusive, so the last day of the range is dropped.
    return start <= day < end
