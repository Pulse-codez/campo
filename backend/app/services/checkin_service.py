"""Monthly check-in window rules.

Writing opens in the last 7 days of each month. Any earlier month that has no check-in yet can
still be written (catch-up). Each month accepts one check-in.
"""

import calendar
from dataclasses import dataclass
from datetime import date

WINDOW_DAYS = 7
CATCH_UP_MONTHS = 3


def period_of(day: date) -> str:
    return f"{day.year:04d}-{day.month:02d}"


def _shift_months(day: date, months: int) -> date:
    total = day.year * 12 + (day.month - 1) + months
    return date(total // 12, total % 12 + 1, 1)


def is_open_now(period: str, today: date) -> bool:
    current = period_of(today)
    if period == current:
        last_day = calendar.monthrange(today.year, today.month)[1]
        return today.day > last_day - WINDOW_DAYS
    return period < current


def writable_periods(today: date, submitted: set[str]) -> list[str]:
    """Periods the student can write for today: this month in the window, plus recent missed months."""
    periods: list[str] = []
    current = period_of(today)
    if is_open_now(current, today) and current not in submitted:
        periods.append(current)
    for back in range(1, CATCH_UP_MONTHS + 1):
        candidate = period_of(_shift_months(today, -back))
        if candidate not in submitted:
            periods.append(candidate)
    return periods


@dataclass(frozen=True)
class WindowCheck:
    allowed: bool
    reason: str | None


def check_writable(period: str, today: date, submitted: set[str]) -> WindowCheck:
    if period in submitted:
        return WindowCheck(False, "already_submitted")
    current = period_of(today)
    if period > current:
        return WindowCheck(False, "period_in_future")
    if period < period_of(_shift_months(today, -CATCH_UP_MONTHS)):
        return WindowCheck(False, "period_too_old")
    if period == current and not is_open_now(period, today):
        return WindowCheck(False, "opens_in_last_week_of_month")
    return WindowCheck(True, None)
