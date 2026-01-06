"""Market data placeholders.

These functions mimic underlying quotes and basic greeks so the API can run
without a live IB connection. Replace them with `ib_insync` tick subscriptions
for production.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict


@dataclass
class UnderlyingQuote:
    price: float
    iv30: float
    timestamp: datetime


@dataclass
class OptionQuote:
    bid: float
    ask: float
    last: float
    delta: float
    iv: float
    oi: int
    volume: int


def fetch_underlying_quote(ticker: str) -> UnderlyingQuote:
    # Stubbed SPY-like quote
    return UnderlyingQuote(price=475.25, iv30=0.18, timestamp=datetime.utcnow())


def fetch_option_quotes(ticker: str, expiry: str) -> Dict[float, OptionQuote]:
    # Keyed by strike
    strikes = [470, 472, 475, 477, 480]
    return {
        strike: OptionQuote(
            bid=1.0 + (strike - 470) * 0.02,
            ask=1.1 + (strike - 470) * 0.02,
            last=1.05 + (strike - 470) * 0.02,
            delta=0.05 * (1 + idx * 0.4),
            iv=0.17 + idx * 0.01,
            oi=800 - idx * 50,
            volume=500 - idx * 40,
        )
        for idx, strike in enumerate(strikes)
    }
