from __future__ import annotations

from typing import Dict, List, Tuple

from app.models.schemas import Bias, LiquidityFilters


def build_liquidity_score(liquidity: LiquidityFilters) -> float:
    # Placeholder heuristic between 0 and 1
    base = 1 - min(liquidity.maxBidAskPct, 1)
    oi_bonus = 0.1 if liquidity.minOI > 100 else 0
    volume_bonus = 0.1 if liquidity.minVolume > 50 else 0
    return min(1.0, max(0.0, base + oi_bonus + volume_bonus))


def compute_probabilities(short_strike: float, request) -> Dict[str, float]:
    # Simplified probability: use delta proxy adjusted by bias
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
    credit_conservative: float,
    max_loss: float,
    liquidity_score: float,
    bias: Bias,
    p_win: float,
    p_loss: float,
    has_earnings: bool,
) -> Tuple[float, float, float, float, float, List[str]]:
    expected_profit = credit_conservative * p_win
    expected_loss = max_loss * p_loss
    ev = expected_profit - expected_loss
    ror = credit_conservative / max_loss if max_loss else 0

    bias_alignment = 0.1 if bias in (Bias.bullish, Bias.bearish) else 0
    earnings_penalty = -0.05 if has_earnings else 0

    score = (
        ev * 0.4
        + ror * 0.25
        + liquidity_score * 0.2
        + bias_alignment * 0.1
        + earnings_penalty * 0.05
    )

    why = [
        f"p(win)={p_win:.2f}",
        f"EV={ev:.3f}",
        f"RoR={ror:.2f}",
        f"Liquidity={liquidity_score:.2f}",
    ]
    if has_earnings:
        why.append("earnings penalty applied")

    return ev, expected_profit, expected_loss, ror, score, why
