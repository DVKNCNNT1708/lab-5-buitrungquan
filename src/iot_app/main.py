"""
FastAPI IoT Ingestion Service
Lab 05: Docker Compose Readiness
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any

import requests
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IoT Ingestion Service",
    description="Lab 05: Docker Compose Readiness",
    version=os.getenv("SERVICE_VERSION", "1.0.0"),
)

SERVICE_NAME = os.getenv("SERVICE_NAME", "iot-service")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "lab05-secret-token")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:9000")


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class ReadingRequest(BaseModel):
    device_id: str = Field(..., description="Device identifier")
    metric: str = Field(..., description="Metric name")
    value: float = Field(..., description="Metric value")
    unit: str = Field(default="", description="Unit of measurement")


class ReadingResponse(BaseModel):
    reading_id: str
    status: str
    ai_result: Optional[Dict[str, Any]] = None


def verify_token(authorization: Optional[str] = Header(None)) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    parts = authorization.split()

    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = parts[1]

    if token != AUTH_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")

    return token


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
    )


@app.post("/readings", response_model=ReadingResponse, tags=["Readings"])
async def create_reading(
    reading: ReadingRequest,
    token: str = Depends(verify_token),
) -> ReadingResponse:
    reading_id = str(uuid.uuid4())

    ai_payload = {
        "device_id": reading.device_id,
        "metric": reading.metric,
        "value": reading.value,
        "unit": reading.unit,
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        response = requests.post(
            f"{AI_SERVICE_URL}/predict",
            json=ai_payload,
            timeout=5,
        )

        if response.status_code == 200:
            ai_result = response.json()
        else:
            ai_result = {
                "label": "unknown",
                "confidence": 0.0,
            }

    except requests.RequestException:
        ai_result = {
            "label": "ai-service-unavailable",
            "confidence": 0.0,
        }

    return ReadingResponse(
        reading_id=reading_id,
        status="created",
        ai_result=ai_result,
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "IoT Ingestion Service Lab 05",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "endpoints": [
            "GET /health",
            "POST /readings",
        ],
    }