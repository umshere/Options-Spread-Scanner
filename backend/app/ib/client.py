"""Thin client wrapper for Interactive Brokers connectivity.

This module is intentionally stubbed to enable local development without an
active IB Gateway/TWS session. Replace the placeholder methods with real
`ib_insync` calls when wiring to live market data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class IBConnection:
    host: str = "127.0.0.1"
    port: int = 7497
    client_id: int = 1


class IBClient:
    def __init__(self, connection: Optional[IBConnection] = None) -> None:
        self.connection = connection or IBConnection()
        self.connected = False

    def connect(self) -> None:
        """Simulate a connection to IB.

        In production, use ib_insync's `IB` instance and handle retries/pacing.
        """
        self.connected = True

    def disconnect(self) -> None:
        self.connected = False

    def is_connected(self) -> bool:
        return self.connected
