# Risk Model Overview

This document summarizes the simplified probability and risk assumptions used by the Options Spread Scanner. The code uses deterministic placeholders to enable development without a live Interactive Brokers (IB) connection.

## Probability of Profit/Loss
- **Primary input**: Implied volatility (IV) from IB option market data.
- **Fallback**: Short-leg option delta magnitude (|delta|) when IV-derived probabilities are unavailable.
- **Method**: Convert IV and DTE into a lognormal probability estimate of finishing beyond the short strike. When unavailable, use `1 - |delta|` as a proxy probability of expiring out-of-the-money.

## Expected Value (EV)
For each spread candidate:
```
EV = (credit_conservative * p_win) - (max_loss * p_loss)
```
- `credit_conservative` is a haircut to mid-price to account for fill slippage.
- `p_loss = 1 - p_win` unless earnings or illiquidity penalties increase the effective loss chance.

## Return on Risk (RoR)
```
RoR = credit_conservative / max_loss
```
Uses conservative credit to align with realistic fills.

## Liquidity Scoring
- Baseline score from bid/ask percentage width, open interest, and volume.
- Penalty applied if bid/ask > configured threshold or if OI/volume fall below minimums.

## Earnings Risk
- If earnings occur before expiry, either block the candidate (default) or apply a penalty to `p_win` and the composite score.

## Composite Score
Weighted sum of:
- EV (weight 0.4)
- RoR (weight 0.25)
- Liquidity score (weight 0.2)
- Bias alignment / regime match (weight 0.1)
- Earnings penalty (weight -0.05 by default)

Weights are heuristic and should be tuned with historical outcomes or trader feedback.

## Exit Plan Heuristics
- **Profit take**: default 70% of max credit or when remaining credit < 30% of original.
- **Sideways exit**: trigger if theta decay stalls below a configurable threshold.
- **Loss exit**: trigger when current debit reaches 1.5× the original credit or when probability of loss exceeds 50%.

## Next Steps
- Backtest probabilities vs realized outcomes to calibrate weights.
- Add scenario analysis for gap/volatility shocks near earnings.
- Incorporate regime classification (trend/vol) to adjust bias alignment scoring.
