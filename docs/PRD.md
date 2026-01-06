# Options Spread Scanner (IB) — PRD

## Summary
Build a decision-support app that scans short-dated options (0–7 DTE) via Interactive Brokers, generates vertical credit spreads (put credit / call credit), ranks them by risk-adjusted attractiveness using probabilities + EV, and outputs a clear entry + exit plan. The app is informational (no auto-trading).

## Target User
Retail or semi-pro options seller who trades short DTE spreads (often SPY) and wants:
- fast screening
- objective ranking
- clear risk management exits
- earnings/event risk protection

## Core Features (MVP)
### Inputs
- Ticker (default SPY)
- Max DTE (0–7)
- Short-leg |delta| max (default 0.10)
- Spread widths allowed (e.g., [1,2,5])
- Min credit (optional)
- Liquidity thresholds (max bid/ask, min OI/volume)
- Earnings filter: default OFF (reject if earnings before expiry)
- Bias: Auto / Bullish / Bearish / Neutral

### Outputs per candidate spread
- Type: Put Credit / Call Credit
- Expiration, strikes, width
- Credit (mid + conservative estimate)
- Max loss, collateral
- Return on risk (RoR)
- Breakeven
- P(win), P(loss) (IV-based, delta as fallback)
- Expected profit, expected loss, EV
- Liquidity score
- Earnings risk flag (ER)
- Suggested exit plan:
  - profit take
  - sideways/stagnation exit
  - loss stop (price-based + probability-based option)

### Ranking
Rank by weighted score:
- EV
- RoR
- Liquidity
- Bias alignment (sentiment/regime)
- Event/Earnings penalty

## Data Sources
- Interactive Brokers (live):
  - Underlying quotes
  - Options chain (expirations/strikes)
  - Option bid/ask/last, OI/volume
  - Greeks/IV via market data ticks
  - Earnings date via contract details (for single names)

Optional later:
- News/sentiment provider (Finnhub/AlphaVantage) + regime classification

## User Flow
1. Dashboard (regime + alerts)
2. Configure scan (or choose preset)
3. Scan results: two tabs (Put Credit / Call Credit)
4. Click candidate → details + payoff + risk + exit plan
5. User manually executes in IB (copy-friendly order ticket details)

## Non-Goals (MVP)
- Auto-trading
- Portfolio margin / multi-leg combos beyond 2-leg verticals
- Full backtesting suite (later phase)

## Risk & Compliance Notes
- Informational/educational tool; no guarantee.
- Display assumptions (fills, probability model, IV source).
- Strong options risk disclosures.

## Success Metrics
- Scan completes within <10s for SPY
- Users can find trades matching rules in <30s
- Exit plan reduces large losses vs discretionary holding
