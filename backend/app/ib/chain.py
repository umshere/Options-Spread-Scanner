"""Option chain helpers (stubbed)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import List


def list_expirations(max_dte: int) -> List[date]:
    today = date.today()
    return [today + timedelta(days=days) for days in range(1, max_dte + 1)]


def list_strikes(reference_price: float, width: float = 1.0, span: int = 5) -> List[float]:
    base = round(reference_price / width) * width
    return [base + offset * width for offset in range(-span, span + 1)]
