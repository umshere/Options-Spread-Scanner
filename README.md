# Options Spread Scanner (IB)

Scans 0–7 DTE vertical credit spreads (put/call) via Interactive Brokers, computes probability + expected value (EV), and provides a risk-first exit plan. This repo currently ships a FastAPI backend with stubbed market data so you can develop locally without IB access.

## Repository layout
- `docs/` – PRD, API contract, architecture notes, and risk model assumptions.
- `backend/` – FastAPI app plus IB/spread modules (stubbed for now).
- `frontend/` – placeholder for a future Next.js UI.

## MVP features (planned)
- IB live chain + Greeks
- Spread generation (vertical put/call credit)
- Liquidity filters
- Earnings risk filter
- Ranking by EV/RoR/liquidity
- Exit plan: profit / sideways / loss

## Running the backend (local)
1. Start IB Gateway/TWS and enable API access (for live mode).
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. Launch the API:
   ```bash
   uvicorn app.main:app --reload
   ```

The `/scan` endpoint will return deterministic sample data until IB connectivity is wired up.

## API quickstart
- Health check: `GET /health`
- Scan spreads: `POST /scan` with the payload defined in `docs/API.md`.

## Disclaimer
This is not financial advice. Options involve significant risk.
