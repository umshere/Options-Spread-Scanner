from __future__ import annotations

from datetime import datetime
from typing import Dict

from fastapi import FastAPI

from app.models.schemas import HealthResponse, Regime, ScanRequest, ScanResponse, ScanResults
from app.spreads.generate import generate_spreads

app = FastAPI(title="Options Spread Scanner", version="0.1.0")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.utcnow())


@app.post("/scan", response_model=ScanResponse)
def scan(request: ScanRequest) -> ScanResponse:
    candidates: Dict[str, list] = generate_spreads(request)
    regime = Regime(trend="sideways", vol="neutral")

    return ScanResponse(
        ticker=request.ticker,
        timestamp=datetime.utcnow(),
        regime=regime,
        results=ScanResults(**candidates),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
