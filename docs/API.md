# API

## POST /scan
Request:
{
  "ticker": "SPY",
  "maxDte": 7,
  "shortDeltaMax": 0.10,
  "spreadWidths": [1,2,5],
  "minCredit": 0.10,
  "allowEarnings": false,
  "bias": "auto",
  "liquidity": {
    "maxBidAskPct": 0.15,
    "minOI": 200,
    "minVolume": 50
  }
}

Response:
{
  "ticker": "SPY",
  "timestamp": "...",
  "regime": {"trend":"sideways", "vol":"neutral"},
  "results": {
    "putCredit": [SpreadCandidate...],
    "callCredit": [SpreadCandidate...]
  }
}

SpreadCandidate:
{
  "type": "PUT_CREDIT",
  "expiry": "2026-01-09",
  "shortStrike": 475,
  "longStrike": 473,
  "width": 2,
  "creditMid": 0.42,
  "creditConservative": 0.35,
  "maxLoss": 1.65,
  "collateral": 165,
  "ror": 0.212,
  "breakeven": 474.58,
  "pWin": 0.86,
  "pLoss": 0.14,
  "expectedProfit": 0.301,
  "expectedLoss": 0.231,
  "ev": 0.070,
  "liquidityScore": 0.82,
  "earningsRisk": {"hasEarnings": false, "daysToEarnings": null, "blocked": false},
  "exitPlan": {
    "profitTakePct": 0.7,
    "sidewaysExit": {"enabled": true, "thetaStallThreshold": 0.10},
    "lossExit": {"mode": "creditMultiple", "value": 1.5}
  },
  "score": 0.74,
  "why": ["short |delta| <= 0.10", "good liquidity", "positive EV", "no earnings risk"]
}
