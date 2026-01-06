from __future__ import annotations

from datetime import date
from typing import Dict, List

from app.ib.chain import list_expirations, list_strikes
from app.ib.marketdata import fetch_underlying_quote
from app.models.schemas import Bias, EarningsRisk, ExitPlan, LiquidityFilters, ScanRequest, SpreadCandidate
from app.spreads.exits import build_exit_plan
from app.spreads.score import build_liquidity_score, compute_probabilities, compute_scores


def _filter_liquidity(liquidity: LiquidityFilters, bid: float, ask: float, oi: int, volume: int) -> bool:
    mid = (bid + ask) / 2
    bid_ask_pct = (ask - bid) / mid if mid else 1.0
    return (
        bid_ask_pct <= liquidity.maxBidAskPct
        and oi >= liquidity.minOI
        and volume >= liquidity.minVolume
    )


def _earnings_stub(allow_earnings: bool) -> EarningsRisk:
    # Stub: assume no earnings risk unless blocked by config
    return EarningsRisk(hasEarnings=False, daysToEarnings=None, blocked=not allow_earnings)


def _build_candidate(
    spread_type: str,
    expiry: date,
    short_strike: float,
    long_strike: float,
    credit_mid: float,
    liquidity_score: float,
    request: ScanRequest,
    exit_plan: ExitPlan,
) -> SpreadCandidate:
    width = abs(short_strike - long_strike)
    credit_conservative = credit_mid * 0.85
    max_loss = width - credit_conservative
    collateral = max_loss * 100
    prob = compute_probabilities(short_strike=short_strike, request=request)
    breakeven = short_strike - credit_conservative if spread_type == "PUT_CREDIT" else short_strike + credit_conservative
    ev, expected_profit, expected_loss, ror, score, why = compute_scores(
        credit_conservative=credit_conservative,
        max_loss=max_loss,
        liquidity_score=liquidity_score,
        bias=request.bias,
        p_win=prob["p_win"],
        p_loss=prob["p_loss"],
        has_earnings=False,
    )
    earnings_risk = _earnings_stub(request.allowEarnings)
    return SpreadCandidate(
        type=spread_type,
        expiry=expiry,
        shortStrike=short_strike,
        longStrike=long_strike,
        width=width,
        creditMid=credit_mid,
        creditConservative=credit_conservative,
        maxLoss=max_loss,
        collateral=collateral,
        ror=ror,
        breakeven=breakeven,
        pWin=prob["p_win"],
        pLoss=prob["p_loss"],
        expectedProfit=expected_profit,
        expectedLoss=expected_loss,
        ev=ev,
        liquidityScore=liquidity_score,
        earningsRisk=earnings_risk,
        exitPlan=exit_plan,
        score=score,
        why=why,
    )


def generate_spreads(request: ScanRequest) -> Dict[str, List[SpreadCandidate]]:
    quote = fetch_underlying_quote(request.ticker)
    expirations = list_expirations(request.maxDte)
    bias = request.bias if request.bias != Bias.auto else Bias.neutral
    candidates: Dict[str, List[SpreadCandidate]] = {"putCredit": [], "callCredit": []}

    for expiry in expirations:
        dte = (expiry - date.today()).days
        if dte <= 0 or dte > request.maxDte:
            continue
        strikes = list_strikes(quote.price, width=min(request.spreadWidths))
        for width in request.spreadWidths:
            for strike in strikes:
                short_strike_put = strike
                long_strike_put = strike - width
                short_strike_call = strike
                long_strike_call = strike + width

                credit_mid_put = max(0.15, min(1.5, width * 0.8))
                credit_mid_call = max(0.12, min(1.3, width * 0.75))

                liquidity_score = build_liquidity_score(liquidity=request.liquidity)
                exit_plan_put = build_exit_plan(width=width, credit=credit_mid_put)
                exit_plan_call = build_exit_plan(width=width, credit=credit_mid_call)

                if request.minCredit and credit_mid_put < request.minCredit:
                    continue
                if request.minCredit and credit_mid_call < request.minCredit:
                    continue

                # Simplified liquidity filter
                if not _filter_liquidity(
                    liquidity=request.liquidity,
                    bid=credit_mid_put - 0.05,
                    ask=credit_mid_put + 0.05,
                    oi=300,
                    volume=200,
                ):
                    continue

                put_candidate = _build_candidate(
                    spread_type="PUT_CREDIT",
                    expiry=expiry,
                    short_strike=short_strike_put,
                    long_strike=long_strike_put,
                    credit_mid=credit_mid_put,
                    liquidity_score=liquidity_score,
                    request=request.copy(update={"bias": bias}),
                    exit_plan=exit_plan_put,
                )
                call_candidate = _build_candidate(
                    spread_type="CALL_CREDIT",
                    expiry=expiry,
                    short_strike=short_strike_call,
                    long_strike=long_strike_call,
                    credit_mid=credit_mid_call,
                    liquidity_score=liquidity_score,
                    request=request.copy(update={"bias": bias}),
                    exit_plan=exit_plan_call,
                )
                candidates["putCredit"].append(put_candidate)
                candidates["callCredit"].append(call_candidate)

    return candidates
