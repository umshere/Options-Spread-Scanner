from __future__ import annotations

from datetime import datetime, date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, conlist, confloat


class Bias(str, Enum):
    auto = "auto"
    bullish = "bullish"
    bearish = "bearish"
    neutral = "neutral"


class LiquidityFilters(BaseModel):
    maxBidAskPct: confloat(ge=0, le=1) = Field(..., description="Max bid/ask width as percent of mid")
    minOI: int = Field(..., description="Minimum open interest")
    minVolume: int = Field(..., description="Minimum daily volume")


class ScanRequest(BaseModel):
    ticker: str = Field("SPY", description="Underlying symbol")
    maxDte: int = Field(7, description="Maximum days to expiration")
    shortDeltaMax: confloat(gt=0, lt=1) = Field(
        0.10, description="Maximum absolute delta for the short option"
    )
    spreadWidths: conlist(int, min_items=1) = Field(
        ..., description="Allowed vertical widths in dollars"
    )
    minCredit: Optional[confloat(gt=0)] = Field(
        None, description="Optional minimum credit filter"
    )
    allowEarnings: bool = Field(
        False, description="Whether to allow spreads that cross an earnings event"
    )
    bias: Bias = Field(Bias.auto, description="Directional bias override")
    liquidity: LiquidityFilters


class Regime(BaseModel):
    trend: str
    vol: str


class EarningsRisk(BaseModel):
    hasEarnings: bool
    daysToEarnings: Optional[int]
    blocked: bool


class SidewaysExit(BaseModel):
    enabled: bool
    thetaStallThreshold: float


class LossExit(BaseModel):
    mode: str
    value: float


class ExitPlan(BaseModel):
    profitTakePct: float
    sidewaysExit: SidewaysExit
    lossExit: LossExit


class SpreadCandidate(BaseModel):
    type: str
    expiry: date
    shortStrike: float
    longStrike: float
    width: float
    creditMid: float
    creditConservative: float
    maxLoss: float
    collateral: float
    ror: float
    breakeven: float
    pWin: float
    pLoss: float
    expectedProfit: float
    expectedLoss: float
    ev: float
    liquidityScore: float
    earningsRisk: EarningsRisk
    exitPlan: ExitPlan
    score: float
    why: List[str]


class ScanResults(BaseModel):
    putCredit: List[SpreadCandidate]
    callCredit: List[SpreadCandidate]


class ScanResponse(BaseModel):
    ticker: str
    timestamp: datetime
    regime: Regime
    results: ScanResults


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
