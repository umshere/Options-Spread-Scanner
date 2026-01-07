from __future__ import annotations

from datetime import date
from typing import Dict, List

from app.ib.chain import list_expirations, list_strikes
from app.ib.marketdata import fetch_underlying_quote
from app.models.schemas import Bias, EarningsRisk, ExitPlan, LiquidityFilters, ScanRequest, SpreadCandidate
from app.spreads.constants import CONTRACT_MULTIPLIER, CREDIT_HAIRCUT
from app.spreads.exits import build_exit_plan
from app.spreads.score import build_liquidity_score, compute_probabilities, compute_scores


def _filter_liquidity(liquidity: LiquidityFilters, bid: float, ask: float, oi: int, volume: int) -> bool:
    mid = (bid + ask) / 2
    if mid <= 0:
        return False
    bid_ask_pct = (ask - bid) / mid
    # TODO: Replace stubbed bid/ask/OI/volume with live order book + depth data.
    return (
        bid_ask_pct <= liquidity.maxBidAskPct
        and oi >= liquidity.minOI
        and volume >= liquidity.minVolume
    )


def _earnings_stub(allow_earnings: bool, expiry: date) -> EarningsRisk:
    # TODO: Replace stubbed earnings schedule with corporate actions calendar lookup.
    # For safety, assume an upcoming earnings event in 5 days to exercise blocking logic.
    days_to_earnings = 5
    dte = (expiry - date.today()).days
    occurs_before_expiry = dte >= 0 and days_to_earnings <= dte
    has_earnings = occurs_before_expiry
    blocked = occurs_before_expiry and not allow_earnings
    return EarningsRisk(hasEarnings=has_earnings, daysToEarnings=days_to_earnings, blocked=blocked)


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
    credit_conservative = credit_mid * CREDIT_HAIRCUT
    max_loss = max(0.0, width - credit_conservative)
    collateral = max_loss * CONTRACT_MULTIPLIER
    prob = compute_probabilities(short_strike=short_strike, request=request)
    breakeven = short_strike - credit_conservative if spread_type == "PUT_CREDIT" else short_strike + credit_conservative
    earnings_risk = _earnings_stub(request.allowEarnings, expiry)
    ev, expected_profit, expected_loss, ror, score, why = compute_scores(
        spread_type=spread_type,
        credit_conservative=credit_conservative,
        max_loss=max_loss,
        liquidity_score=liquidity_score,
        bias=request.bias,
        p_win=prob["p_win"],
        p_loss=prob["p_loss"],
        earnings_risk=earnings_risk,
    )
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

                put_meets_credit = request.minCredit is None or credit_mid_put >= request.minCredit
                call_meets_credit = request.minCredit is None or credit_mid_call >= request.minCredit

                # Simplified liquidity filter
                put_liquid = _filter_liquidity(
                    liquidity=request.liquidity,
                    bid=credit_mid_put - 0.05,
                    ask=credit_mid_put + 0.05,
                    oi=300,
                    volume=200,
                )
                call_liquid = _filter_liquidity(
                    liquidity=request.liquidity,
                    bid=credit_mid_call - 0.05,
                    ask=credit_mid_call + 0.05,
                    oi=300,
                    volume=200,
                )

                if put_meets_credit and put_liquid:
                    put_candidate = _build_candidate(
                        spread_type="PUT_CREDIT",
                        expiry=expiry,
                        short_strike=short_strike_put,
                        long_strike=long_strike_put,
                        credit_mid=credit_mid_put,
                        liquidity_score=liquidity_score,
                        request=request.model_copy(update={"bias": bias}),
                        exit_plan=exit_plan_put,
                    )
                    if not put_candidate.earningsRisk.blocked:
                        candidates["putCredit"].append(put_candidate)
                if call_meets_credit and call_liquid:
                    call_candidate = _build_candidate(
                        spread_type="CALL_CREDIT",
                        expiry=expiry,
                        short_strike=short_strike_call,
                        long_strike=long_strike_call,
                        credit_mid=credit_mid_call,
                        liquidity_score=liquidity_score,
                        request=request.model_copy(update={"bias": bias}),
                        exit_plan=exit_plan_call,
                    )
                    if not call_candidate.earningsRisk.blocked:
                        candidates["callCredit"].append(call_candidate)

    return candidates
