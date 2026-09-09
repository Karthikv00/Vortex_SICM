"""
backend/main.py — FastAPI application entry point.

Run locally:
    uvicorn backend.main:app --reload --port 8000

All routes follow docs/architecture/api-contract.md.
Implements: KARTHI-005
"""
from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.routes import explanation, forecast, optimization, scenario, simulation

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Vortex SICM — Queue Simulation & Resource Optimizer",
    description=(
        "JP-012: Bank branch customer arrival queue simulation and "
        "resource allocation optimizer. AAVISHKARA-26."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS — allow frontend dev server (any origin during hackathon)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global error handler — ensures structured error format from api-contract.md
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s", request.url)
    return JSONResponse(
        status_code=500,
        content={
            "detail": {
                "error": "internal_server_error",
                "message": "An unexpected server error occurred",
            }
        },
    )
# ---------------------------------------------------------------------------
# Health check — FR-API-1
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health() -> dict:
    """Service liveness check."""
    return {"status": "ok"}

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(scenario.router, prefix="/api", tags=["Scenario"])
app.include_router(forecast.router, prefix="/api", tags=["Forecast"])
app.include_router(simulation.router, prefix="/api", tags=["Simulation"])
app.include_router(optimization.router, prefix="/api", tags=["Optimization"])
app.include_router(explanation.router, prefix="/api", tags=["Explanation"])


# ---------------------------------------------------------------------------
# Dev entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
