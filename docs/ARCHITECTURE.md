# Architecture Overview

The project is split into an API-oriented backend and a future frontend. The backend is intentionally modular so that Interactive Brokers (IB) connectivity, spread generation, scoring, and exit logic can evolve independently.

## High-Level Components
- **API layer (FastAPI)**: Exposes `/scan` and health endpoints. Validates input, orchestrates data fetch → spread generation → scoring → exit plan construction.
- **IB client adapters**: Lightweight wrappers around `ib_insync` for connecting to IB Gateway/TWS, fetching option chains, and retrieving quotes/greeks. These live under `app/ib/` and are written so they can be mocked in tests and replaced later with real-time adapters.
- **Spread engine**: Generates put/call credit spreads from option chains and applies user constraints (DTE, width, credit, liquidity). Housed under `app/spreads/`.
- **Scoring + risk model**: Computes probability of profit/loss, EV, return on risk, and a composite score. Lives in `app/spreads/score.py` with helpers in `app/spreads/exits.py` and `docs/RISK_MODEL.md` for the methodology.
- **Storage**: Stubbed `app/storage/db.py` for optional persistence/caching.
- **Frontend**: Placeholder directory for a future Next.js UI that will consume the API.

## Request Flow
1. **Input validation** using Pydantic models in `app/models/schemas.py`.
2. **Market data fetch** through `ib/marketdata.py` and `ib/chain.py` (currently stubbed) to obtain expirations, strikes, and quotes.
3. **Spread generation** via `spreads/generate.py`, yielding candidate put and call credit spreads within max DTE, width, and credit thresholds.
4. **Scoring** in `spreads/score.py` to evaluate EV, RoR, liquidity, bias alignment, and penalties (e.g., earnings risk).
5. **Exit plans** defined in `spreads/exits.py` to suggest profit-take, sideways, and loss stops.
6. **Response assembly** in `main.py` returning structured candidates and reasoning.

## Error Handling & Assumptions
- The stub uses deterministic sample data to enable local development without IB access.
- Real IB integration should handle connection retries, pacing violations, and partial data availability gracefully.
- Probability estimates fall back to option delta when IV is missing.

## Extensibility Notes
- Replace stubbed functions in `ib/` with real `ib_insync` calls.
- Swap the in-memory placeholder scoring with a more robust model (see `docs/RISK_MODEL.md`).
- Add Redis/Postgres caching by implementing persistence in `storage/db.py` and wiring it into market data fetches.
- Extend `/scan` to stream progress or allow preset templates for common tickers.
