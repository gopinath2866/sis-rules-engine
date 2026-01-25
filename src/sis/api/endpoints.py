"""
FastAPI endpoints for SIS engine
"""

import time
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from ..main import scan_files
from .schemas import HealthResponse, ScanRequest, ScanResponse

# Create FastAPI app
app = FastAPI(
    title="SIS Rules Engine API",
    description="Security Isolation Standard Rules Validation API",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track startup time
startup_time = time.time()


@app.get("/health")
async def health_check() -> HealthResponse:
    uptime = time.time() - startup_time
    return HealthResponse(status="healthy", version="1.0.0", uptime=uptime)


@app.post("/validate", response_model=ScanResponse)
async def validate_files(request: ScanRequest, http_request: Request) -> ScanResponse:
    try:
        # Extract client IP for rate limiting
        client_ip = http_request.client.host if http_request.client else "unknown"

        # Scan files
        response = scan_files(
            files=request.files,
            client_id=client_ip,
            rate_limit=False,  # Disable rate limiting for now
        )

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/rules")
async def get_rules() -> dict:
    from ..main import load_rules

    try:
        rules = load_rules()
        return {"rules": rules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load rules: {str(e)}")
