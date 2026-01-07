from __future__ import annotations

from typing import Dict, List, Tuple

from app.models.schemas import Bias, EarningsRisk, LiquidityFilters
from app.spreads.constants import (
    BIAS_ALIGNMENT_BONUS,
    BIAS_MISALIGNMENT_PENALTY,
    BIAS_WEIGHT,
    EARNINGS_SCORE_PENALTY,
    EARNINGS_WEIGHT,
    EV_WEIGHT,
    LIQUIDITY_WEIGHT,
    ROR_WEIGHT,
)


def build_liquidity_score(liquidity: LiquidityFilters) -> float:
    # Placeholder heuristic between 0 and 1
    base = 1 - min(liquidity.maxBidAskPct, 1)
    oi_bonus = 0.1 if liquidity.minOI > 100 else 0
    volume_bonus = 0.1 if liquidity.minVolume > 50 else 0
    return min(1.0, max(0.0, base + oi_bonus + volume_bonus))


def compute_probabilities(short_strike: float, request) -> Dict[str, float]:
    # Simplified probability: use delta proxy adjusted by bias
    # TODO: Replace with calibrated probability of touch/expire ITM using IV surface.
    base_delta = min(request.shortDeltaMax, 0.5)
    bias_adjustment = {
        Bias.bullish: 0.05,
        Bias.bearish: -0.05,
        Bias.neutral: 0.0,
        Bias.auto: 0.0,
    }[request.bias]

    p_win = max(0.0, min(1.0, 1 - base_delta + bias_adjustment))
    p_loss = 1 - p_win
    return {"p_win": p_win, "p_loss": p_loss}


def compute_scores(
    spread_type: str,
    credit_conservative: float,
    max_loss: float,
    liquidity_score: float,
    bias: Bias,
    p_win: float,
    p_loss: float,
    earnings_risk: EarningsRisk,
) -> Tuple[float, float, float, float, float, List[str]]:
    expected_profit = credit_conservative * p_win
    expected_loss = max_loss * p_loss
    ev = expected_profit - expected_loss
    ror = credit_conservative / max_loss if max_loss else 0

    bias_alignment = 0.0
    if bias == Bias.bullish and spread_type == "PUT_CREDIT":
        bias_alignment = BIAS_ALIGNMENT_BONUS
    elif bias == Bias.bearish and spread_type == "CALL_CREDIT":
        bias_alignment = BIAS_ALIGNMENT_BONUS
    elif bias in (Bias.bullish, Bias.bearish):
        bias_alignment = BIAS_MISALIGNMENT_PENALTY

    earnings_penalty = EARNINGS_SCORE_PENALTY if earnings_risk.hasEarnings else 0

    score = (
        ev * EV_WEIGHT
        + ror * ROR_WEIGHT
        + liquidity_score * LIQUIDITY_WEIGHT
        + bias_alignment * BIAS_WEIGHT
        + earnings_penalty * EARNINGS_WEIGHT
    )
    # TODO: Add score normalization across expirations/underlyings to improve comparability.

    why = [
        f"p(win)={p_win:.2f}",
        f"EV={ev:.3f}",
        f"RoR={ror:.2f}",
        f"Liquidity={liquidity_score:.2f}",
    ]
    if earnings_risk.hasEarnings:
        why.append("earnings penalty applied")

    return ev, expected_profit, expected_loss, ror, score, why
